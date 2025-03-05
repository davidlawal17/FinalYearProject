// src/components/PropertyList.js
import React, { useState, useEffect } from 'react';
import PropertyCard from './PropertyCard';
import './PropertyList.css';

const PropertyList = () => {
  const [properties, setProperties] = useState([]);
  const [filters, setFilters] = useState({ location: '', min_price: '', max_price: '', property_type: '' });

  const fetchProperties = async () => {
    const query = new URLSearchParams(filters).toString();
    const response = await fetch(`/api/properties?${query}`);
    const data = await response.json();
    setProperties(data);
  };

  useEffect(() => {
    fetchProperties();
  }, []);

  const handleFilterChange = (e) => {
    setFilters({ ...filters, [e.target.name]: e.target.value });
  };

  const handleSearch = () => {
    fetchProperties();
  };

  return (
    <div className="property-list-container">
      <h1>Find Your Next Investment</h1>
      <div className="filter-bar">
        <input type="text" name="location" placeholder="Location (e.g., London)" onChange={handleFilterChange} />
        <input type="number" name="min_price" placeholder="Min Price (£)" onChange={handleFilterChange} />
        <input type="number" name="max_price" placeholder="Max Price (£)" onChange={handleFilterChange} />
        <select name="property_type" onChange={handleFilterChange}>
          <option value="">All Types</option>
          <option value="House">House</option>
          <option value="Flat">Flat</option>
          <option value="Bungalow">Bungalow</option>
          <option value="Terraced">Terraced</option>
        </select>
        <button onClick={handleSearch}>Search</button>
      </div>

      <div className="property-grid">
        {properties.map((property) => (
          <PropertyCard key={property.id} property={property} />
        ))}
      </div>
    </div>
  );
};

export default PropertyList;
