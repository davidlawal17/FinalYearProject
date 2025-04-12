import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom';
import { useAuth } from '../context/AuthContext';
import './PropertyCard.css';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Tooltip,
  Legend
} from 'chart.js';
import { Line, Bar } from 'react-chartjs-2';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, Tooltip, Legend);

const InvestmentModal = ({ isOpen, onClose, isLoading, recommendation, investmentDetails }) => {
  if (!isOpen) return null;

  const benchmarkGrowth = investmentDetails?.benchmark_growth ?? 3.5;
  const benchmarkROI = investmentDetails?.benchmark_roi ?? 7.5;
  const growthThreshold = investmentDetails?.growth_threshold ?? 4.5;
  const showLineChart = investmentDetails?.show_growth_chart;
  const showBarChart = investmentDetails?.show_roi_chart;

  const generateBenchmarkLine = (startValue, years, annualGrowth = 0.035) => {
    const result = [];
    for (let i = 0; i < years; i++) {
      result.push(Math.round(startValue * Math.pow(1 + annualGrowth, i)));
    }
    return result;
  };

  const getExplanationMessage = () => {
    if (!recommendation) return "";
    const rec = recommendation.toLowerCase();
    const growth = investmentDetails?.growth_rate;
    const roi = investmentDetails?.roi;

    if (showLineChart) {
      if (rec.includes("buy")) {
        return `This property's projected value is growing faster than the market average. Consider buying for strong returns.`;
      } else {
        return `This property's value grows slower than the market benchmark (${benchmarkGrowth}%) or may not meet investment criteria. Avoid or investigate further.`;
      }
    } else if (showBarChart) {
      if (rec.includes("buy") && roi > benchmarkROI) {
        return `Although growth is weaker than market average (${growth}% vs ${benchmarkGrowth}%), the ROI is strong at ${roi}%, well above the benchmark ROI of ${benchmarkROI}%.`;
      } else if (rec.includes("avoid") && growth < growthThreshold) {
        return `Although ROI is strong at ${roi}%, the growth rate of ${growth}% is too weak compared to the required threshold of ${growthThreshold}%. Avoid unless other factors are favorable.`;
      } else if (rec.includes("avoid") && roi < benchmarkROI) {
        return `Despite a strong growth rate of ${growth}%, the ROI is only ${roi}%, which is below the benchmark of ${benchmarkROI}%. This suggests it may not be a worthwhile investment.`;
      } else if (rec.includes("buy") && roi < benchmarkROI) {
        return `Growth rate of ${growth}% exceeds expectations, justifying a buy despite ROI of ${roi}% being near or below the benchmark ROI of ${benchmarkROI}%.`;
      } else {
        return `The model's recommendation is based on a mix of growth and ROI factors.`;
      }
    }
  };

  return ReactDOM.createPortal(
    <div className="overlay">
      <div className="modal">
        {isLoading ? (
          <div className="spinner"></div>
        ) : (
          <>
            <h2>Investr's Advice</h2>
            <p><strong>Recommendation:</strong> {recommendation}</p>
            <p><strong>Estimated Monthly Rent:</strong> £{investmentDetails?.estimated_rent || ""}</p>
            <p><strong>Growth Rate:</strong> {investmentDetails?.growth_rate || ""}%</p>
            <p><strong>ROI:</strong> {investmentDetails?.roi || ""}%</p>
            <p><strong>Why this recommendation?</strong><br />{getExplanationMessage()}</p>

            {showLineChart && Array.isArray(investmentDetails?.price_projection) ? (
              <div style={{ width: '100%' }}>
                <Line
                  data={{
                    labels: investmentDetails.price_projection.map((_, i) => `Year ${i}`),
                    datasets: [
                      {
                        label: 'Projected Value (£)',
                        data: investmentDetails.price_projection,
                        borderColor: '#7FB3D5',
                        tension: 0.3
                      },
                      {
                        label: `Benchmark (${benchmarkGrowth}% Growth)`,
                        data: generateBenchmarkLine(
                          investmentDetails.price_projection[0],
                          investmentDetails.price_projection.length,
                          benchmarkGrowth / 100
                        ),
                        borderColor: '#E67E22',
                        borderDash: [5, 5],
                        tension: 0.3
                      }
                    ]
                  }}
                  options={{
                    responsive: true,
                    plugins: {
                      legend: { display: true },
                      tooltip: {
                        mode: 'index',
                        intersect: false,
                        callbacks: {
                          label: context => `£${context.parsed.y.toLocaleString()}`
                        }
                      }
                    },
                    scales: {
                      x: { ticks: { color: '#EAEDED' } },
                      y: { ticks: { color: '#EAEDED' } }
                    }
                  }}
                />
              </div>
            ) : showBarChart ? (
              <div style={{ width: '100%' }}>
                <Bar
                  data={{
                    labels: ['ROI (%)', 'Benchmark ROI (%)'],
                    datasets: [
                      {
                        label: 'ROI Comparison',
                        data: [investmentDetails.roi, benchmarkROI],
                        backgroundColor: ['#2ECC71', '#E67E22']
                      }
                    ]
                  }}
                  options={{
                    responsive: true,
                    plugins: {
                      legend: { display: false },
                      title: { display: true, text: 'ROI vs Benchmark ROI' }
                    },
                    scales: {
                      y: {
                        beginAtZero: true,
                        ticks: { color: '#EAEDED' }
                      },
                      x: {
                        ticks: { color: '#EAEDED' }
                      }
                    }
                  }}
                />
              </div>
            ) : null}

            <button onClick={onClose}>Close</button>
          </>
        )}
      </div>
    </div>,
    document.body
  );
};


const PropertyCard = ({ property, savedProperties = [], isFavouritePage = false, onRemoveFavourite }) => {
  const { user } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [recommendation, setRecommendation] = useState(null);
  const [investmentDetails, setInvestmentDetails] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const isSaved = savedProperties.some(saved => saved.id === property.id);
  const isOwner = user?.firebase_uid && property.created_by === user.firebase_uid;

  useEffect(() => {
    console.group('Property Ownership Details');
    console.log('Property Data:', property);
    console.log('Ownership Match:', property.created_by === user?.firebase_uid);
    console.groupEnd();
  }, [property, user?.firebase_uid]);

  const handleSave = async () => {
    if (!user) return alert('Please log in to save properties.');
    setIsLoading(true);
    setError(null);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/favourites', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
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
    if (!user) return alert('Please log in to remove properties.');
    setIsLoading(true);
    setError(null);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/favourites', {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
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
      const response = await fetch(`/api/properties/${property.id}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
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

  const handleInvestmentAdvice = async () => {
    setIsModalOpen(true);
    setIsLoading(true);
    setRecommendation(null);
    setInvestmentDetails(null);

    const body = {
      title: property.title,
      price: property.price,
      bedrooms: property.bedrooms,
      bathrooms: property.bathrooms,
      sizeSqFeetMax: property.sizeSqFeetMax || 600,
      property_type: property.property_type || "Other"
    };

    try {
      const response = await fetch('/api/recommend', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      });

      const result = await response.json();

      setRecommendation(result.recommendation
        ? `${result.recommendation} (${result.confidence}% confidence)`
        : "Unable to generate recommendation.");

     setInvestmentDetails({
      roi: result.roi,
      estimated_rent: result.estimated_rent,
      growth_rate: result.growth_rate,
      price_projection: result.price_projection,
      benchmark_growth: result.benchmark_growth,
      benchmark_roi: result.benchmark_roi,
      growth_threshold: result.growth_threshold,
      show_growth_chart: result.show_growth_chart,
      show_roi_chart: result.show_roi_chart,
      explanation: result.explanation
    });


    } catch (err) {
      console.error("Recommendation Error:", err);
      setRecommendation("Something went wrong. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="property-card">
      <img
        src={property.image_url || "/images/properties/defaultprop.jpg"}
        alt={property.title}
        className="property-image"
      />
      <div className="property-details">
        <h3>{property.title}</h3>
        <p className="property-price">£{property.price?.toLocaleString() || 'N/A'}</p>
        <div className="property-features">
          <span> {property.bedrooms} bed</span>
          <span> {property.bathrooms} bath</span>
          <span> {property.property_type}</span>
        </div>
        <p className="property-location"> {property.location}</p>
        <p className="property-description">{property.description}</p>
      </div>

      <div className="property-actions">
        {!isSaved && user && !isFavouritePage && (
          <button onClick={handleSave} disabled={isLoading} className="save-button">
            {isLoading ? 'Saving...' : 'Save Property'}
          </button>
        )}
        {isFavouritePage && (
          <button onClick={handleRemove} disabled={isLoading} className="remove-button">
            {isLoading ? 'Removing...' : 'Remove'}
          </button>
        )}
        {isOwner && (
          <button onClick={handleDelete} disabled={isLoading} className="delete-button">
            {isLoading ? 'Deleting...' : 'Delete Property'}
          </button>
        )}
        <button onClick={handleInvestmentAdvice} className="recommendation-button">
           Get Investment Advice
        </button>
      </div>

      <InvestmentModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        isLoading={isLoading}
        recommendation={recommendation}
        investmentDetails={investmentDetails}
      />

      {error && <div className="error-message">{error}</div>}
    </div>
  );
};

export default PropertyCard;
