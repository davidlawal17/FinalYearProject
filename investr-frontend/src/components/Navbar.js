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
        {user ? (
          <>
            <li><Link to="/favourites">View Favourites</Link></li>
            <li><button onClick={handleLogout}>Logout</button></li>
          </>
        ) : null}
      </ul>
    </nav>
  );
};

export default Navbar;
