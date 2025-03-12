// src/App.js
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import Home from './components/Home';
import Login from './components/Login';
import Register from './components/Register';
import Dashboard from './components/Dashboard';
import PropertyList from './components/PropertyList';
import Favourites from './components/Favourites';
import Recommender from './components/Recommender';    // Placeholder or actual component
import Simulation from './components/Simulation';      // Placeholder or actual component
import NewsFeed from './components/NewsFeed';          // Placeholder or actual component
import { useAuth } from './context/AuthContext';
import './index.css';
import backgroundImage from './assets/background-image.jpg';

const App = () => {
  const { user } = useAuth();

  const appStyle = {
    backgroundImage: `linear-gradient(rgba(0, 31, 63, 0.9), rgba(0, 58, 92, 0.9)), url(${backgroundImage})`,
    backgroundSize: 'cover',
    backgroundPosition: 'center',
    backgroundAttachment: 'fixed',
    minHeight: '100vh',
    color: '#EAEDED',
  };

  return (
    <div style={appStyle}>
      <Router>
        <Navbar />
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<Home />} />
          <Route path="/properties" element={<PropertyList />} />

          {/* Authenticated Routes */}
          <Route path="/favourites" element={user ? <Favourites /> : <Navigate to="/login" />} />
          <Route path="/dashboard" element={user ? <Dashboard /> : <Navigate to="/login" />} />
          <Route path="/recommender" element={user ? <Recommender /> : <Navigate to="/login" />} />
          <Route path="/simulation" element={user ? <Simulation /> : <Navigate to="/login" />} />
          <Route path="/news" element={user ? <NewsFeed /> : <Navigate to="/login" />} />

          {/* Authentication Routes */}
          <Route path="/login" element={!user ? <Login /> : <Navigate to="/dashboard" />} />
          <Route path="/register" element={!user ? <Register /> : <Navigate to="/dashboard" />} />

          {/* Catch-all */}
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </Router>
    </div>
  );
};

export default App;
