import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import './PropertyCard.css';

const PropertyCard = ({ property, savedProperties = [], isFavouritePage = false, onRemoveFavourite }) => {
  const { user } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const isSaved = savedProperties.some(saved => saved.id === property.id);

  const logOwnershipDetails = () => {
    console.group('Property Ownership Details');
    console.log('Property Data:', property);
    console.log('Current User:', user);
    console.log('Property created_by:', property.created_by);
    console.log('User firebase_uid:', user?.firebase_uid);
    console.log('Ownership Match:', property.created_by === user?.firebase_uid);
    console.groupEnd();
  };

  const handleSave = async () => {
    if (!user) {
      alert('Please log in to save properties.');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const token = localStorage.getItem('token');
      if (!token) throw new Error('Authentication token not found');

      const response = await fetch('/api/favourites', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ property_id: property.id })
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.error || 'Failed to save property');

      alert('Saved to favourites!');
    } catch (err) {
      console.error('Save Error:', err);
      setError(err.message);
      alert(`Error: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRemove = async () => {
    if (!user) {
      alert('Please log in to remove properties.');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const token = localStorage.getItem('token');
      if (!token) throw new Error('Authentication token not found');

      const response = await fetch('/api/favourites', {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ property_id: property.id })
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.error || 'Failed to remove property');

      alert('Removed from favourites!');
      onRemoveFavourite(property.id);
    } catch (err) {
      console.error('Remove Error:', err);
      setError(err.message);
      alert(`Error: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async () => {
    const confirmDelete = window.confirm("Are you sure you want to permanently delete this property?");
    if (!confirmDelete) return;

    setIsLoading(true);
    setError(null);

    try {
      const token = localStorage.getItem('token');
      if (!token) throw new Error('Authentication token not found');

      const response = await fetch(`/api/properties/${property.id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.error || 'Failed to delete property');

      alert('Property deleted successfully!');
      window.location.reload();
    } catch (err) {
      console.error('Delete Error:', err);
      setError(err.message);
      alert(`Error: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    logOwnershipDetails();
  }, []);

  const isOwner = user?.firebase_uid && property.created_by === user.firebase_uid;

  return (
    <div className="property-card">
      <img
        src={property.image_url || "/images/properties/defaultprop.jpg"}
        alt={property.title}
        className="property-image"
      />
      <div className="property-details">
        <h3>{property.title}</h3>
        <p className="property-price">£{property.price.toLocaleString()}</p>
        <div className="property-features">
          <span>🏠 {property.bedrooms} bed</span>
          <span>🚿 {property.bathrooms} bath</span>
          <span>📐 {property.property_type}</span>
        </div>
        <p className="property-location">📍 {property.location}</p>
        <p className="property-description">{property.description}</p>
      </div>

      <div className="property-actions">
        {!isSaved && user && !isFavouritePage && (
          <button onClick={handleSave} disabled={isLoading} className="save-button">
            {isLoading ? 'Saving...' : '❤️ Save Property'}
          </button>
        )}
        {isFavouritePage && (
          <button onClick={handleRemove} disabled={isLoading} className="remove-button">
            {isLoading ? 'Removing...' : '🗑️ Remove'}
          </button>
        )}
        {isOwner && (
          <button onClick={handleDelete} disabled={isLoading} className="delete-button">
            {isLoading ? 'Deleting...' : '❌ Delete Property'}
          </button>
        )}
      </div>

      {error && <div className="error-message">{error}</div>}

      {/*process.env.NODE_ENV === 'development' && (
        <div className="debug-info">
          <p><strong>Debug Info:</strong></p>
          <p>Property ID: {property.id}</p>
          <p>Created By: {property.created_by || 'null'}</p>
          <p>Current User: {user?.firebase_uid || 'Not logged in'}</p>
          <p>Ownership: {isOwner ? ' You own this' : ' Not yours'}</p>
        </div>
      )*/}
    </div>
  );
};

export default PropertyCard;
