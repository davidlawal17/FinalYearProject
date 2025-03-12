// src/components/Login.js
import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Auth.css';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

     const data = await response.json();

    if (response.ok) {
      localStorage.setItem('token', data.access_token); // Store JWT token
      login(data.user); // Set user in context
      navigate('/dashboard'); // Redirect to dashboard
    } else {
      alert(`Login failed: ${data.error || 'Invalid credentials'}`);
    }
  } catch (error) {
    alert('An unexpected error occurred during login.');
  }
};

  return (
    <div className="auth-container">
      <h2>Sign In</h2>
      <form onSubmit={handleLogin} className="auth-form">
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <button type="submit">Login</button>
      </form>
      {/* Message with link to register */}
      <p className="auth-message">
        Haven't got an account? <Link to="/register">Create one</Link>
      </p>
    </div>
  );
};

export default Login;
