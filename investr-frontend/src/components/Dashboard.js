// src/components/Dashboard.js
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Dashboard.css';

const Dashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  const goTo = (path) => navigate(path);

  return (
    <div className="dashboard-container">
      <h1>Welcome back, {user?.email}!</h1>
      <p>Select a feature to get started:</p>

      <div className="dashboard-buttons">
        <button onClick={() => goTo('/properties')}>🏡 Property Search & Filter</button>
        <button onClick={() => goTo('/favourites')}>❤️ Saved Favourites</button>
        <button onClick={() => goTo('/recommender')}>🤖 Recommender System</button>
        <button onClick={() => goTo('/simulation')}>📊 Investment Simulation</button>
        <button onClick={() => goTo('/news')}>📰 Market News</button>
      </div>
    </div>
  );
};

export default Dashboard;
