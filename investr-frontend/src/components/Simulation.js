// src/components/Simulation.js
import React, { useState } from 'react';
import './Simulation.css'; // Create this next for styling

const Simulation = () => {
  const [formData, setFormData] = useState({
    property_price: '',
    down_payment: '',
    mortgage_rate: '',
    rental_income: '',
    appreciation_rate: '',
    years: '',
  });

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setResult(null);
    setLoading(true);

    try {
      const response = await fetch('/api/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.error || 'Simulation failed');
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="simulation-container">
      <h2>Investment Simulation</h2>
      <form onSubmit={handleSubmit} className="simulation-form">
        {[
          { name: 'property_price', label: 'Property Price (£)' },
          { name: 'down_payment', label: 'Down Payment (£)' },
          { name: 'mortgage_rate', label: 'Mortgage Rate (%)' },
          { name: 'rental_income', label: 'Monthly Rental Income (£)' },
          { name: 'appreciation_rate', label: 'Annual Appreciation Rate (%)' },
          { name: 'years', label: 'Investment Horizon (Years)' },
        ].map((field) => (
          <div key={field.name} className="form-group">
            <label>{field.label}</label>
            <input
              type="number"
              name={field.name}
              value={formData[field.name]}
              onChange={handleChange}
              required
            />
          </div>
        ))}
        <button type="submit" disabled={loading}>
          {loading ? 'Simulating...' : 'Run Simulation'}
        </button>
      </form>

      {error && <div className="error">{error}</div>}

      {result && (
        <div className="results">
          <h3>Results</h3>
          <p>📈 Future Property Value: £{result.future_value.toLocaleString()}</p>
          <p>💰 Total Rental Income: £{result.total_rent_income.toLocaleString()}</p>
          <p>🏦 Total Mortgage Paid: £{result.total_mortgage_paid.toLocaleString()}</p>
          <p>📊 Net Profit: £{result.net_profit.toLocaleString()}</p>
          <p>🔁 Annual Cash Flow: £{result.annual_cashflow.toLocaleString()}</p>
          <p>📉 ROI: {result.roi.toFixed(2)}%</p>
        </div>
      )}
    </div>
  );
};

export default Simulation;
