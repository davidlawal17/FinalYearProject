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
    custom_appreciation_rate: '',
    years: '',
    mortgage_term: 2,
    market_outlook: 'baseline',
  });

  const [result, setResult] = useState(null);
  const [ltv, setLTV] = useState(null);
  const [mortgageRate, setMortgageRate] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showRentInfo, setShowRentInfo] = useState(false);
  const [showAppreciationInfo, setShowAppreciationInfo] = useState(false);
  const [showMarketInfo, setShowMarketInfo] = useState(false);

  const baseRateTable = {
    '95': { 1: 5.65, 2: 5.57, 3: 5.45, 4: 5.38, 5: 5.34, 6: 5.40, 7: 5.44, 8: 5.49, 9: 5.52, 10: 5.55 },
    '90': { 1: 5.25, 2: 5.12, 3: 5.00, 4: 4.95, 5: 4.88, 6: 4.93, 7: 4.96, 8: 5.00, 9: 5.02, 10: 5.05 },
    '85': { 1: 4.90, 2: 4.79, 3: 4.70, 4: 4.68, 5: 4.67, 6: 4.70, 7: 4.72, 8: 4.75, 9: 4.77, 10: 4.80 },
    '75': { 1: 4.70, 2: 4.62, 3: 4.57, 4: 4.56, 5: 4.55, 6: 4.57, 7: 4.59, 8: 4.61, 9: 4.62, 10: 4.65 },
    '60': { 1: 4.30, 2: 4.23, 3: 4.22, 4: 4.21, 5: 4.20, 6: 4.22, 7: 4.23, 8: 4.24, 9: 4.25, 10: 4.26 }
  };

  const marketAdjustment = {
    optimistic: -0.25,
    baseline: 0,
    pessimistic: 0.25
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
    const years = parseInt(formData.mortgage_term);

    if (!price || deposit >= price || !years) {
      setLTV(null);
      setMortgageRate(null);
      return;
    }

    const loan = price - deposit;
    const ltvCalc = (loan / price) * 100;
    const band = getLTVBand(ltvCalc);
    const baseRate = baseRateTable[band]?.[years] ?? 5.5;
    const marketAdj = marketAdjustment[formData.market_outlook] || 0;
    const finalRate = (baseRate + marketAdj).toFixed(2);

    setLTV(ltvCalc.toFixed(2));
    setMortgageRate(finalRate);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    if (parseFloat(value) < 0) return;

    const updated = { ...formData, [name]: value };

    if (name === 'appreciation_rate' && value !== 'custom') {
      updated.custom_appreciation_rate = '';
    }

    setFormData(updated);

    if ([
      'property_price', 'down_payment_percent', 'mortgage_term', 'market_outlook'
    ].includes(name)) {
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

    const appreciation_rate = formData.appreciation_rate === 'custom'
      ? parseFloat(formData.custom_appreciation_rate)
      : parseFloat(formData.appreciation_rate);

    try {
      const payload = {
        ...formData,
        down_payment,
        mortgage_rate: mortgageRate,
        appreciation_rate
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
    const growth = formData.appreciation_rate === 'custom'
      ? parseFloat(formData.custom_appreciation_rate)
      : parseFloat(formData.appreciation_rate);

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
          <span className="info-circle" onClick={() => setShowRentInfo(!showRentInfo)}>i</span>
        </label>
        <input
          type="number"
          min="0"
          step="25"
          name="rental_income"
          value={formData.rental_income}
          onChange={handleChange}
          required
        />
        {showRentInfo && (
          <div className="form-note">
            💡 Rent is typically 0.8%–1.1% of the property's value. For example, on a £500,000 property, expected rent is £333–£458/month. In London, yields range between 2.05%–6.04%.
          </div>
        )}
      </div>

      <div className="form-group">
        <label>
          Appreciation Rate (%)
          <span className="info-circle" onClick={() => setShowAppreciationInfo(!showAppreciationInfo)}>i</span>
        </label>
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
            name="custom_appreciation_rate"
            value={formData.custom_appreciation_rate}
            onChange={handleChange}
            required
          />
        )}
        {showAppreciationInfo && (
          <div className="form-note">
            📈 The current annual appreciation rate is 2.3% (Jan 2025). Forecasts suggest this may rise to 3.5% by 2026. Use custom to test your own rate.
          </div>
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
        <label>Mortgage Term (Years)</label>
        <select name="mortgage_term" value={formData.mortgage_term} onChange={handleChange}>
          {[...Array(10)].map((_, i) => (
            <option key={i + 1} value={i + 1}>
              {i + 1}-Year Fixed
            </option>
          ))}
        </select>
      </div>

      <div className="form-group">
        <label>
          Market Outlook
          <span className="info-circle" onClick={() => setShowMarketInfo(!showMarketInfo)}>i</span>
        </label>
        <select name="market_outlook" value={formData.market_outlook} onChange={handleChange}>
          <option value="optimistic">Optimistic (rates falling)</option>
          <option value="baseline">Baseline</option>
          <option value="pessimistic">Pessimistic (rates rising)</option>
        </select>
        {showMarketInfo && (
          <div className="form-note">
            📉 <strong>Market Outlook explained:</strong> This setting adjusts your <strong>initial interest rate</strong>, based on economic expectations.
            <ul style={{ marginTop: '0.5rem', paddingLeft: '1.2rem' }}>
              <li><strong>Optimistic</strong>: Lenders expect rates to drop → base rate reduced by 0.25%.</li>
              <li><strong>Baseline</strong>: No change to base rate (0%).</li>
              <li><strong>Pessimistic</strong>: Lenders expect rates to rise → base rate increased by 0.25%.</li>
            </ul>
            This is a <strong>one-time adjustment</strong> applied at the start. It does not change year by year.
            <br />
            📊 Example: If your base rate is 5.00% → Optimistic = 4.75%, Baseline = 5.00%, Pessimistic = 5.25%.
            <br /><br />
            <strong>LTV (Loan-to-Value)</strong> affects your base rate: a lower LTV (larger deposit) usually gets better rates.
          </div>
        )}
      </div>

      {ltv && mortgageRate && (
        <div className="info-box">
          <p>
            🧮 <strong>LTV:</strong> {ltv}% — Estimated {formData.mortgage_term}-year fixed rate:{' '}
            <strong>{mortgageRate}%</strong>
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
          <Bar
            data={generateBarChartData()}
            options={{
              responsive: true,
              plugins: { legend: { labels: { color: '#fff' } } },
              scales: {
                x: { ticks: { color: '#ccc' } },
                y: { ticks: { color: '#ccc' } }
              }
            }}
          />
        </div>
      </div>
    )}
  </div>
);
};

export default Simulation;
