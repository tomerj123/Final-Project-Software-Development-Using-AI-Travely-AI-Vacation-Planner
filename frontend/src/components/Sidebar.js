// frontend/src/components/Sidebar.js

import React from 'react';
import { NavLink } from 'react-router-dom';
import '../index.css'; // Assuming you have a Sidebar.css file for styles

const Sidebar = () => {
  return (
    <div className="sidebar">
      <nav className="nav">
        <NavLink to="/" className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}>
          Plan your trip
        </NavLink>
        <NavLink to="/iata-codes" className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}>
          Find IATA Codes
        </NavLink>

      </nav>
    </div>
  );
};

export default Sidebar;
