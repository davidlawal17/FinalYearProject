import React from 'react';
import { useAuth } from '../context/AuthContext';
import './PropertyCard.css';

const PropertyCard = ({ property, savedProperties = [] }) => { //  Default value for savedProperties
    const { user } = useAuth();

    //  Ensure savedProperties is defined before calling .some()
    const isSaved = savedProperties && savedProperties.some(saved => saved.id === property.id);

    const handleSave = async () => {
        if (!user) {
            alert('Please log in to save properties.');
            return;
        }

        const token = localStorage.getItem('token');
        if (!token) {
            alert('Authentication token not found. Please log in again.');
            return;
        }

        try {
            const response = await fetch('/api/favourites', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ property_id: property.id })
            });

            const data = await response.json();
            console.log("DEBUG: Save property API Response:", data);

            if (response.ok) {
                alert('Saved to favourites!');
            } else {
                console.error(" Failed to save property:", data);
                alert(`Failed to save property: ${data.error || "Unexpected error"}`);
            }
        } catch (error) {
            console.error(' Error saving property:', error);
            alert('An error occurred while saving the property.');
        }
    };

    return (
        <div className="property-card">
            <img src={property.image_url} alt={property.title} />
            <h3>{property.title}</h3>
            <p>Price: £{property.price.toLocaleString()}</p>
            <p>Bedrooms: {property.bedrooms} | Bathrooms: {property.bathrooms}</p>
            <p>Type: {property.property_type}</p>
            <p>{property.description}</p>

            {/*  Hide Save Button if already saved */}
            {!isSaved && user && <button onClick={handleSave}>Save Property</button>}
        </div>
    );
};

export default PropertyCard;
