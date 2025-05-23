// src/components/AddProperty.js
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './AddProperty.css';

const AddProperty = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    title: '',
    price: '',
    location: '',
    bedrooms: '',
    bathrooms: '',
    property_type: '',
    description: '',
    image: null,
  });

  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value, files } = e.target;
    if (name === 'image') {
      setFormData({ ...formData, image: files[0] });
    } else {
      setFormData({ ...formData, [name]: value });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const token = localStorage.getItem('token');
    if (!token) {
      alert('You must be logged in to add a property.');
      return;
    }

    const data = new FormData();
    for (const key in formData) {
      data.append(key, formData[key]);
    }

    setLoading(true);

    try {
      const response = await fetch('/api/properties', {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`
        },
        body: data
      });

      const result = await response.json();

      if (response.ok) {
        alert('Property added successfully!');
        setFormData({
          title: '',
          price: '',
          location: '',
          bedrooms: '',
          bathrooms: '',
          property_type: '',
          description: '',
          image: null,
        });
        navigate('/properties');
      } else {
        alert(`Failed to add property: ${result.error}`);
      }
    } catch (error) {
      console.error('Error submitting property:', error);
      alert('An unexpected error occurred.');
    } finally {
      setLoading(false);
    }
  };

  const generatePriceOptions = (start, end, step) => {
    const options = [];
    for (let price = start; price <= end; price += step) {
      options.push(<option key={price} value={price}>£{price.toLocaleString()}</option>);
    }
    return options;
  };

  return (
    <div className="add-property-container">
      <h2>Add New Property</h2>
      <form onSubmit={handleSubmit} className="add-property-form">
        <input type="text" name="title" placeholder="Title" value={formData.title} onChange={handleChange} required />

        {/* Location Dropdown */}
        <label>Location:</label>
        <select name="location" value={formData.location} onChange={handleChange} required>
          <option value="">Select Location</option>
          <option value="Central London">Central London</option>
          <option value="North London">North London</option>
          <option value="East London">East London</option>
          <option value="West London">West London</option>
          <option value="South London">South London</option>
        </select>

        {/* Price Dropdowns */}
        <label>Price:</label>
        <select name="price" value={formData.price} onChange={handleChange} required>
          <option value="">Select Price</option>
          {generatePriceOptions(50000, 1000000, 25000)}
          {generatePriceOptions(1100000, 10000000, 100000)}
        </select>

        <input type="number" name="bedrooms" placeholder="Bedrooms" value={formData.bedrooms} onChange={handleChange} required min="0" />
        <input type="number" name="bathrooms" placeholder="Bathrooms" value={formData.bathrooms} onChange={handleChange} required min="0" />

        <label>Property Type:</label>
        <select name="property_type" value={formData.property_type} onChange={handleChange} required>
          <option value="">Select Type</option>
          <option value="House">House</option>
          <option value="Flat">Flat</option>
          <option value="Bungalow">Bungalow</option>
          <option value="Terraced">Terraced</option>
        </select>

        <textarea name="description" placeholder="Description" value={formData.description} onChange={handleChange} required />

        <label>Upload Image:</label>
        <input type="file" name="image" accept="image/*" onChange={handleChange} />

        <button type="submit" disabled={loading}>{loading ? 'Adding Property...' : 'Add Property'}</button>
      </form>
    </div>
  );
};

export default AddProperty;
