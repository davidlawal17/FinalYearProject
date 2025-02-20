import React from 'react';
import { useAuth } from '../context/AuthContext';
import './Dashboard.css';

const Dashboard = () => {
  const { user } = useAuth();

  return (
    <div className="dashboard-container">
      <h1>Welcome to Your Dashboard, {user?.email}!</h1>
      <p>Features coming soon....</p>
    </div>
  );
};

export default Dashboard;
