import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import PropertyCard from './PropertyCard';
import './Favourites.css';

const Favourites = () => {
    const { user } = useAuth();
    const [favourites, setFavourites] = useState([]);

    const fetchFavourites = async () => {
        if (!user) {
            console.error(" No user found in context.");
            return;
        }

        const token = localStorage.getItem('token');
        console.log("DEBUG: JWT Token:", token);  //  Log the token

        try {
            const response = await fetch('/api/favourites', {
                headers: { Authorization: `Bearer ${token}` }
            });

            const data = await response.json();
            console.log("DEBUG: Favourites API Response:", data);

            if (response.ok && Array.isArray(data)) {
                setFavourites(data);
            } else {
                console.error(" Error fetching favourites:", data.error);
            }
        } catch (error) {
            console.error(" Fetch error:", error);
        }
    };

    useEffect(() => {
        fetchFavourites();
    }, [user]);

    return (
        <div className="favourites-container">
            <h1>Your Saved Properties</h1>
            {favourites.length > 0 ? (
                <div className="property-grid">
                    {favourites.map((property) => (
                        <PropertyCard key={property.id} property={property} savedProperties={favourites || []} />
                    ))}
                </div>
            ) : (
                <p>No properties saved yet. Start saving now!</p>
            )}
        </div>
    );
};

export default Favourites;
