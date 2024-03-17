// frontend/src/components/TripForm.js

import React, { useState } from 'react';
import '../index.css';
import logo from "../logo1.svg";
import spinner from "../spinner.gif";
const TripForm = ({ setTripPlanHtml }) => {
    const [loading, setLoading] = useState(false);
  const [formState, setFormState] = useState({
    origin: '',
    originIATA: '',  // State for origin IATA code
    destination: '',
    destinationIATA: '',  // State for destination IATA code
    budget: '',
    startDate: '',
    endDate: '',
      people: '',
  });

  const [errors, setErrors] = useState({});

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormState(prevState => ({
      ...prevState,
      [name]: value
    }));

    // Clear error when user modifies the input
    if (errors[name]) {
      setErrors(prevErrors => ({
        ...prevErrors,
        [name]: null
      }));
    }
  };

  const validateForm = () => {
    const newErrors = {};
    // IATA codes validation: must be either 3 characters long or empty
    if (formState.originIATA && formState.originIATA.length !== 3) {
      newErrors.originIATA = 'Preferred Airport Code must be 3 characters';
    }
    if (formState.destinationIATA && formState.destinationIATA.length !== 3) {
      newErrors.destinationIATA = 'Preferred Airport Code must be 3 characters';
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateForm()) return;
    setLoading(true);
    // Convert camelCase to snake_case for the backend
    const payload = {
        origin: formState.origin,
        origin_iata: formState.originIATA,  // Adjusted
        destination: formState.destination,
        destination_iata: formState.destinationIATA,  // Adjusted
        budget: parseInt(formState.budget, 10), // Make sure budget is an integer
        start_date: formState.startDate,  // Adjusted
        end_date: formState.endDate,  // Adjusted
        num_of_people: formState.people,
    };

    try {
        const response = await fetch('http://tomerandsionefinalproject.eastus.azurecontainer.io/plan-trip/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload),  // Use the adjusted payload
        });

        const data = await response.text();  // Assuming the backend responds with text/html

        if (!response.ok) {
            console.error('Validation errors:', data);
            throw new Error(`Validation failed: ${data}`);
        }

        setTripPlanHtml(data);  // Assuming you want to display the HTML content received
        setLoading(false);
    } catch (error) {
        console.error('Failed to fetch trip plan:', error);
        setLoading(false);
    }
};



  return (
      <div>
          <header className="app-header">
              <img src={logo} alt="Travely logo" className="app-logo"/>
          </header>
          <div className="trip-form-container">
              <h2>Plan Trip</h2>
              <form onSubmit={handleSubmit} className="trip-form">
                  <input
                      type="text"
                      name="origin"
                      value={formState.origin}
                      onChange={handleChange}
                      placeholder="Origin City"
                      required
                  /><br/>
                  <input
                      type="text"
                      name="originIATA"
                      value={formState.originIATA}
                      onChange={handleChange}
                      placeholder="Preferred Origin Airport Code"
                  /><br/>
                  {errors.originIATA && <p style={{color: 'red'}}>{errors.originIATA}</p>}
                  <input
                      type="text"
                      name="destination"
                      value={formState.destination}
                      onChange={handleChange}
                      placeholder="Destination City"
                      required
                  /><br/>
                  <input
                      type="text"
                      name="destinationIATA"
                      value={formState.destinationIATA}
                      onChange={handleChange}
                      placeholder="Preferred Destination Airport Code"
                  /><br/>
                  {errors.destinationIATA && <p style={{color: 'red'}}>{errors.destinationIATA}</p>}
                  <input
                      type="number"
                      name="budget"
                      value={formState.budget}
                      onChange={handleChange}
                      placeholder="Budget"
                      required
                  /><br/>
                  <input
                      type="date"
                      name="startDate"
                      value={formState.startDate}
                      onChange={handleChange}
                      required
                  /><br/>
                  <input
                      type="date"
                      name="endDate"
                      value={formState.endDate}
                      onChange={handleChange}
                      required
                  /><br/>
                  <input
                      type="number"
                      name="people"
                      value={formState.people}
                      onChange={handleChange}
                      placeholder="Number of People"
                      required
                  /><br/>
                  <button type="submit">Plan Trip</button>
              </form>
              {loading && (
                  <div className="loading-container">
                      <img src={spinner} alt="Loading..."/>
                  </div>
              )}
          </div>
      </div>
  );
};

export default TripForm;
