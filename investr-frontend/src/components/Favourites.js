import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import PropertyCard from './PropertyCard';
import './Favourites.css';

const Favourites = () => {
  const { user } = useAuth();
  const [favourites, setFavourites] = useState([]);

  useEffect(() => {
    const fetchFavourites = async () => {
      if (!user) return;

      const response = await fetch('/api/favourites', {
        headers: { Authorization: `Bearer ${user.token}` }
      });

      const data = await response.json();
      setFavourites(data);
    };

    fetchFavourites();
  }, [user]);

  return (
    <div className="favourites-container">
      <h1>Your Saved Properties</h1>
      {favourites.length > 0 ? (
        <div className="property-grid">
          {favourites.map((property) => (
            <PropertyCard key={property.id} property={property} />
          ))}
        </div>
      ) : (
        <p>No properties saved yet. Start saving now!</p>
      )}
    </div>
  );
};

export default Favourites;
