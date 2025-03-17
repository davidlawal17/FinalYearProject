import React from 'react';
import { useAuth } from '../context/AuthContext';
import './PropertyCard.css';

const PropertyCard = ({ property, savedProperties = [], isFavouritePage = false, onRemoveFavourite }) => {
    const { user } = useAuth();
    const isSaved = savedProperties.some(saved => saved.id === property.id);

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

    const handleRemove = async () => {
        if (!user) {
            alert('Please log in to remove properties.');
            return;
        }

        const token = localStorage.getItem('token');
        if (!token) {
            alert('Authentication token not found. Please log in again.');
            return;
        }

        try {
            const response = await fetch('/api/favourites', {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ property_id: property.id })
            });

            const data = await response.json();
            console.log("DEBUG: Remove property API Response:", data);

            if (response.ok) {
                alert('Removed from favourites!');
                onRemoveFavourite(property.id); //  Update UI after removal
            } else {
                console.error(" Failed to remove property:", data);
                alert(`Failed to remove property: ${data.error || "Unexpected error"}`);
            }
        } catch (error) {
            console.error(' Error removing property:', error);
            alert('An error occurred while removing the property.');
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

            {/* Show "Save Property" button only if it's not already saved */}
            {!isSaved && user && !isFavouritePage && <button onClick={handleSave}>Save Property</button>}

            {/* Show "Remove from Favourites" button only on the Favourites page */}
            {isFavouritePage && <button onClick={handleRemove} className="remove-button">Remove from Favourites</button>}
        </div>
    );
};

export default PropertyCard;
