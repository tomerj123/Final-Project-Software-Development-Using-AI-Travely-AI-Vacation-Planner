// frontend/src/App.js
import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import TripForm from './components/TripForm';
import IATACodes from './components/IATACodes';
import TripPlan from './components/TripPlan'; // Ensure this component correctly handles rendering HTML content
import './App.css';

function App() {
  const [tripPlanHtml, setTripPlanHtml] = useState('');

  return (
    <Router>
      <div style={{ display: "flex" }}>
        <Sidebar />
        <div style={{ flex: 1, padding: "20px" }}>
          <Routes>
            <Route path="/" element={!tripPlanHtml && <TripForm setTripPlanHtml={setTripPlanHtml} />} />
            <Route path="/iata-codes" element={<IATACodes />} />
          </Routes>
          {tripPlanHtml && <TripPlan plan={tripPlanHtml} />}
        </div>
      </div>
    </Router>
  );
}

export default App;
