import React, { useState } from 'react';
import './Simulation.css';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend);

const Simulation = () => {
  const [formData, setFormData] = useState({
    property_price: 80000,
    down_payment_percent: 5,
    rental_income: '',
    appreciation_rate: '2.3',
    years: '',
    mortgage_term: '2'
  });

  const [result, setResult] = useState(null);
  const [ltv, setLTV] = useState(null);
  const [mortgageRate, setMortgageRate] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const rateTable = {
    '95': { '2': 5.57, '5': 5.34 },
    '90': { '2': 5.12, '5': 4.88 },
    '85': { '2': 4.79, '5': 4.67 },
    '75': { '2': 4.62, '5': 4.55 },
    '60': { '2': 4.23, '5': 4.20 }
  };

  const getLTVBand = (ltv) => {
    if (ltv >= 95) return '95';
    if (ltv >= 90) return '90';
    if (ltv >= 85) return '85';
    if (ltv >= 75) return '75';
    return '60';
  };

  const calculateLTVAndRate = () => {
    const price = parseFloat(formData.property_price);
    const deposit = (parseFloat(formData.down_payment_percent) / 100) * price;

    if (!price || deposit >= price) {
      setLTV(null);
      setMortgageRate(null);
      return;
    }

    const loan = price - deposit;
    const ltvCalc = (loan / price) * 100;
    const band = getLTVBand(ltvCalc);
    const rate = rateTable[band][formData.mortgage_term] || 5.5;

    setLTV(ltvCalc.toFixed(2));
    setMortgageRate(rate);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;

    if (parseFloat(value) < 0) return; // prevent negative input

    const updated = { ...formData, [name]: value };
    setFormData(updated);

    if (['property_price', 'down_payment_percent', 'mortgage_term'].includes(name)) {
      setTimeout(() => calculateLTVAndRate(), 0);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setResult(null);
    setLoading(true);

    const price = parseFloat(formData.property_price);
    const down_payment = (parseFloat(formData.down_payment_percent) / 100) * price;

    try {
      const payload = {
        ...formData,
        down_payment,
        mortgage_rate: mortgageRate
      };

      const response = await fetch('/api/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
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

  const generateBarChartData = () => {
    const years = parseInt(formData.years);
    const base = parseFloat(formData.property_price);
    const growth = parseFloat(formData.appreciation_rate);

    const labels = Array.from({ length: years + 1 }, (_, i) => `Year ${i}`);
    const start = Array(years + 1).fill(base);
    const future = Array.from({ length: years + 1 }, (_, i) =>
      base * Math.pow(1 + growth / 100, i)
    );

    return {
      labels,
      datasets: [
        {
          label: 'Starting Value (£)',
          data: start,
          backgroundColor: 'rgba(255, 255, 255, 0.2)',
        },
        {
          label: 'Projected Value (£)',
          data: future,
          backgroundColor: 'rgba(255, 140, 66, 0.8)',
        }
      ]
    };
  };

  return (
    <div className="simulation-container">
      <h2>Investment Simulation</h2>
      <form onSubmit={handleSubmit} className="simulation-form">
        <div className="form-group">
          <label>Property Price (£)</label>
          <input
            type="number"
            min="0"
            step="5000"
            name="property_price"
            value={formData.property_price}
            onChange={handleChange}
            required
          />
        </div>

        <div className="form-group">
          <label>Down Payment (% of Property Price)</label>
          <input
            type="number"
            min="0"
            step="1"
            name="down_payment_percent"
            value={formData.down_payment_percent}
            onChange={handleChange}
            required
          />
        </div>

        <div className="form-group">
          <label>
            Monthly Rental Income (£)
            <span className="tooltip">
              ⓘ <span className="tooltiptext">Typical rent is 0.8%–1.1% of the property's value. For £500K, rent ≈ £333–£458/month.</span>
            </span>
          </label>
          <input
            type="number"
            min="0"
            name="rental_income"
            value={formData.rental_income}
            onChange={handleChange}
            required
          />
        </div>

        <div className="form-group">
          <label>Appreciation Rate (%)</label>
          <select name="appreciation_rate" value={formData.appreciation_rate} onChange={handleChange}>
            <option value="2.3">Current (2.3%)</option>
            <option value="3.5">Forecast (3.5%)</option>
            <option value="custom">Custom</option>
          </select>
          {formData.appreciation_rate === 'custom' && (
            <input
              type="number"
              min="0"
              step="0.1"
              name="appreciation_rate"
              placeholder="Enter custom rate"
              onChange={handleChange}
              required
            />
          )}
        </div>

        <div className="form-group">
          <label>Investment Horizon (Years)</label>
          <input
            type="number"
            name="years"
            min="1"
            value={formData.years}
            onChange={handleChange}
            required
          />
        </div>

        <div className="form-group">
          <label>Mortgage Term (2 or 5 years)</label>
          <select name="mortgage_term" value={formData.mortgage_term} onChange={handleChange}>
            <option value="2">2-Year Fixed</option>
            <option value="5">5-Year Fixed</option>
          </select>
        </div>

        {ltv && mortgageRate && (
          <div className="info-box">
            <p>
              🧮 <strong>LTV:</strong> {ltv}% — Estimated {formData.mortgage_term}-year fixed rate: <strong>{mortgageRate}%</strong>
            </p>
          </div>
        )}

        <button type="submit" disabled={loading || !mortgageRate}>
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

          <div className="chart-container">
            <h3>📊 Property Value vs Starting Price</h3>
            <Bar data={generateBarChartData()} options={{ responsive: true, plugins: { legend: { labels: { color: '#fff' } } }, scales: { x: { ticks: { color: '#ccc' } }, y: { ticks: { color: '#ccc' } } } }} />
          </div>
        </div>
      )}
    </div>
  );
};

export default Simulation;
