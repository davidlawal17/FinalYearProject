// src/components/PropertyList.js
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import PropertyCard from './PropertyCard';
import AddProperty from './AddProperty';
import './PropertyList.css';

const PropertyList = () => {
  const [properties, setProperties] = useState([]);
  const [filters, setFilters] = useState({
    location: '',
    min_price: '',
    max_price: '',
    property_type: ''
  });

  const navigate = useNavigate();

  const fetchProperties = async () => {
    const params = new URLSearchParams();
    if (filters.location) params.append('location', filters.location);
    if (filters.min_price) params.append('min_price', filters.min_price);
    if (filters.max_price) params.append('max_price', filters.max_price);
    if (filters.property_type) params.append('property_type', filters.property_type);

    try {
      const response = await fetch(`/api/properties?${params.toString()}`);
      const data = await response.json();
      setProperties(data);
    } catch (error) {
      console.error("Error fetching properties:", error);
    }
  };

  useEffect(() => {
    fetchProperties();
  }, []);

  const handleInputChange = (e) => {
    setFilters({ ...filters, [e.target.name]: e.target.value });
  };

  return (
    <div className="property-list-container">
      <h1>Find Your Next Investment</h1>

      <div className="filter-bar">
        <select name="location" onChange={handleInputChange} value={filters.location}>
          <option value="">All Areas</option>
          <option value="North London">North London</option>
          <option value="South London">South London</option>
          <option value="East London">East London</option>
          <option value="West London">West London</option>
          <option value="Central London">Central London</option>
        </select>

        <input type="number" name="min_price" placeholder="Min Price (£)" value={filters.min_price} onChange={handleInputChange} min={50000} step={50000} />
        <input type="number" name="max_price" placeholder="Max Price (£)" value={filters.max_price} onChange={handleInputChange} min={1000000} step={100000} />

        <select name="property_type" onChange={handleInputChange} value={filters.property_type}>
          <option value="">All Types</option>
          <option value="House">House</option>
          <option value="Flat">Flat</option>
          <option value="Bungalow">Bungalow</option>
          <option value="Terraced">Terraced</option>
        </select>

        <button onClick={fetchProperties}>Search</button>

        {/* 👉 Add Property Button */}
        <button className="add-property-button" onClick={() => navigate('/add-property')}>
          + Add Property
        </button>
      </div>

      <div className="property-grid">
        {properties.length > 0 ? (
          properties.map((property) => (
            <PropertyCard key={property.id} property={property} />
          ))
        ) : (
          <p>No properties found. Try adjusting filters.</p>
        )}
      </div>
    </div>
  );
};

export default PropertyList;
