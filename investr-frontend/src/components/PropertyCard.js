// src/components/PropertyCard.js
import React from 'react';
import { useAuth } from '../context/AuthContext';
import './PropertyCard.css';

const PropertyCard = ({ property }) => {
  const { user } = useAuth();

  const handleSave = async () => {
    if (!user) return alert('Please log in to save properties.');

    try {
      const response = await fetch('/api/favourites', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ property_id: property.id, user_id: user.uid })
      });

      if (response.ok) {
        alert('Saved to favourites!');
      } else {
        alert('Failed to save property.');
      }
    } catch (error) {
      console.error('Error saving property:', error);
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

      {/* 📌 Save Property Button - Does NOT interfere with filtering */}
      {user && <button onClick={handleSave}>Save Property</button>}
    </div>
  );
};

export default PropertyCard;
