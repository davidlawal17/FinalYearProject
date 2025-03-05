// src/components/PropertyCard.js
import React from 'react';
import { useAuth } from '../context/AuthContext';
import './PropertyCard.css';

const PropertyCard = ({ property }) => {
  const { user } = useAuth();

  const handleSave = async () => {
    if (!user) return alert('Please log in to save properties.');
    await fetch('/api/favourites', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ property_id: property.id, user_id: user.uid })
    });
    alert('Saved to favourites!');
  };

  return (
    <div className="property-card">
      <img src={property.image_url} alt={property.title} />
      <h3>{property.title}</h3>
      <p>£{property.price.toLocaleString()}</p>
      <p>{property.location}</p>
      <p>{property.bedrooms} Beds | {property.bathrooms} Baths | {property.property_type}</p>
      <p>{property.description}</p>
      {user && <button onClick={handleSave}>Save to Favourites</button>}
    </div>
  );
};

export default PropertyCard;
