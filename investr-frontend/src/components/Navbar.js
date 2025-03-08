import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Navbar.css';

const Navbar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <nav className="navbar">
      <div className="logo">Investr</div>
      <ul className="nav-links">
        <li><Link to="/">Home</Link></li>
        {!user ? (
          // Show sign-in when not authenticated
          <li><Link to="/login">Sign In</Link></li>
        ) : (
          <>
            <li><Link to="/favourites">View Favourites</Link></li>  {/* New Favourites Button */}
            <li><button onClick={handleLogout}>Logout</button></li>
          </>
        )}
      </ul>
    </nav>
  );
};

export default Navbar;
