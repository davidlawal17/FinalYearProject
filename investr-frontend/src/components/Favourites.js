// src/components/Favourites.js
import React, { useEffect, useState } from 'react';
import PropertyCard from './PropertyCard';
import { useAuth } from '../context/AuthContext';
import './Favourites.css';

const Favourites = () => {
  const { user } = useAuth();
  const [favourites, setFavourites] = useState([]);

  const fetchFavourites = async () => {
    if (!user) return;
    const response = await fetch(`/api/favourites?user_id=${user.uid}`);
    const data = await response.json();
    setFavourites(data);
  };

  useEffect(() => {
    fetchFavourites();
  }, [user]);

  if (!user) return <p>Please log in to view your favourites.</p>;

  return (
    <div className="favourites-container">
      <h1>Your Saved Properties</h1>
      <div className="property-grid">
        {favourites.map((fav) => (
          <PropertyCard key={fav.property.id} property={fav.property} />
        ))}
      </div>
    </div>
  );
};

export default Favourites;
