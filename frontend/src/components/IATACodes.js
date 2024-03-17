// frontend/src/components/IATACodes.js

import React, { useState } from 'react';
import logo from '../logo1.svg';

const IATACodes = () => {
  const [originCity, setOriginCity] = useState('');
  const [destinationCity, setDestinationCity] = useState('');
  const [iataCodes, setIataCodes] = useState(null);

  const fetchIATACodes = async (event) => {
    event.preventDefault(); // Prevent the default form submit behavior
    try {
      const response = await fetch(`http://tomerandsionefinalproject.eastus.azurecontainer.io/search-for-your-preferred-airports/?origin_city=${originCity}&destination_city=${destinationCity}`);
      if (!response.ok) throw new Error('Network response was not ok');

      const data = await response.json();
      setIataCodes(data);
    } catch (error) {
      console.error('Error fetching IATA codes:', error);
    }
  };

  return (
      <div>
        <header className="app-header">
          <img src={logo} alt="Travely logo" className="app-logo"/>
        </header>
        <div className="trip-form-container">
          <h2>Find IATA Codes</h2>
          <h4>Here you can search for your preferred airports for the trip</h4>
          <form onSubmit={fetchIATACodes} className="trip-form">
            <input
                type="text"
                value={originCity}
                onChange={(e) => setOriginCity(e.target.value)}
                placeholder="Origin City"
            /><br/>
            <input
                type="text"
                value={destinationCity}
                onChange={(e) => setDestinationCity(e.target.value)}
                placeholder="Destination City"
            /><br/>
            <button type="submit">Find Codes</button>
          </form>
          {iataCodes && (
              <div>
                <h3>Results</h3>
                <div>
                  <strong>Origin Airports:</strong>
                  <ul>
                    {iataCodes.origin_city.airports.map((airport) => (
                        <li key={airport['IATA code']}>{airport.Name} ({airport['IATA code']})</li>
                    ))}
                  </ul>
                </div>
                <div>
                  <strong>Destination Airports:</strong>
                  <ul>
                    {iataCodes.destination_city.airports.map((airport) => (
                        <li key={airport['IATA code']}>{airport.Name} ({airport['IATA code']})</li>
                    ))}
                  </ul>
                </div>
              </div>
          )}
        </div>
      </div>
  );
};

export default IATACodes;
