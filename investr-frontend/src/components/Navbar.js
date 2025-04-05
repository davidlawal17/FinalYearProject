import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Navbar.css';

const Navbar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <nav className="navbar">
      <div className="logo">Investr</div>
      <ul className="nav-links">
        {user ? (
          <>
            <li><Link to="/dashboard">Home</Link></li>
            <li><button onClick={handleLogout}>Logout</button></li>
          </>
        ) : (
          location.pathname !== '/login' && (
            <li><Link to="/login">Sign In</Link></li>
          )
        )}
      </ul>
    </nav>
  );
};

export default Navbar;
