// frontend/src/components/TripForm.js

import React, { useState } from 'react';
import '../index.css';
import logo from "../logo1.svg";
import spinner from "../spinner.gif";
import Snackbar from '@mui/material/Snackbar';
import Alert from '@mui/material/Alert';
const TripForm = ({ setTripPlanHtml }) => {
    const [snackbarOpen, setSnackbarOpen] = React.useState(false);
const [snackbarMessage, setSnackbarMessage] = React.useState("");

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
    const currentDate = new Date().toISOString().split('T')[0];
    if (formState.startDate < currentDate) {
        newErrors.startDate = 'Start Date cannot be in the past';
    }

    // End date validation: must not be in the past and not before start date
    if (formState.endDate < currentDate) {
        newErrors.endDate = 'End Date cannot be in the past';
    }
    if (formState.endDate < formState.startDate) {
        newErrors.endDate = 'End Date cannot be before Start Date';
    }
    // Required fields validation
    if (!formState.origin.trim()) {
        newErrors.origin = 'Origin City is required';
    }
    if (!formState.destination.trim()) {
        newErrors.destination = 'Destination City is required';
    }
    if (!formState.startDate) {
        newErrors.startDate = 'Start Date is required';
    }
    if (!formState.endDate) {
        newErrors.endDate = 'End Date is required';
    }
    if (!formState.budget.trim()) {
        newErrors.budget = 'Budget is required';
    } else if (isNaN(formState.budget) || parseInt(formState.budget, 10) <= 0) {
        newErrors.budget = 'Budget must be a positive number';
    }

    // IATA codes validation: must be either 3 characters long
    if (!formState.originIATA.trim()) {
        newErrors.originIATA = 'Preferred Origin Airport Code is required';
    } else if (formState.originIATA.length !== 3) {
        newErrors.originIATA = 'Preferred Origin Airport Code must be 3 characters';
    }
    if (!formState.destinationIATA.trim()) {
        newErrors.destinationIATA = 'Preferred Destination Airport Code is required';
    } else if (formState.destinationIATA.length !== 3) {
        newErrors.destinationIATA = 'Preferred Destination Airport Code must be 3 characters';
    }

    // Number of people validation
    if (!formState.people.trim()) {
        newErrors.people = 'Number of People is required';
    } else {
        const numPeople = parseInt(formState.people, 10);
        if (isNaN(numPeople) || numPeople < 1 || numPeople > 6) {
            newErrors.people = 'Number of People must be between 1 and 6';
        }
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
        console.error( error);
        setLoading(false);
        setSnackbarMessage(error.message);  // Set the error message
        setSnackbarOpen(true);
        console.error( error);
        setLoading(false);
    }
};



return (
    <div>
        <header className="app-header">
            <img src={logo} alt="Travely logo" className="app-logo" />
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
                />
                <br />
                <input
                    type="text"
                    name="originIATA"
                    value={formState.originIATA}
                    onChange={handleChange}
                    placeholder="Preferred Origin Airport Code"
                    required
                />
                {errors.originIATA && <p style={{ color: 'red' }}>{errors.originIATA}</p>} {/* Display error if exists */}
                <br />
                <input
                    type="text"
                    name="destination"
                    value={formState.destination}
                    onChange={handleChange}
                    placeholder="Destination City"
                />
                <br />
                <input
                    type="text"
                    name="destinationIATA"
                    value={formState.destinationIATA}
                    onChange={handleChange}
                    placeholder="Preferred Destination Airport Code"
                    required
                />
                {errors.destinationIATA && <p style={{ color: 'red' }}>{errors.destinationIATA}</p>} {/* Display error if exists */}
                <br />
                <input
                    type="number"
                    name="budget"
                    value={formState.budget}
                    onChange={handleChange}
                    placeholder="Budget"
                    required
                />
                {errors.budget && <p style={{ color: 'red' }}>{errors.budget}</p>} {/* Display error if exists */}
                <br />
                <input
                    type="date"
                    name="startDate"
                    value={formState.startDate}
                    onChange={handleChange}
                    required
                />
                {errors.startDate && <p style={{ color: 'red' }}>{errors.startDate}</p>} {/* Display error if exists */}
                <br />
                <input
                    type="date"
                    name="endDate"
                    value={formState.endDate}
                    onChange={handleChange}
                    required
                />
                {errors.endDate && <p style={{ color: 'red' }}>{errors.endDate}</p>} {/* Display error if exists */}
                <br />
                <input
                    type="number"
                    name="people"
                    value={formState.people}
                    onChange={handleChange}
                    placeholder="Number of People"
                    min="1"
                    max="6"
                    required
                />
                {errors.people && <p style={{ color: 'red' }}>{errors.people}</p>} {/* Display error if exists */}
                <br />
                <button type="submit">Plan Trip</button>
            </form>
            {loading && (
                <div className="loading-container">
                    <img src={spinner} alt="Loading..." />
                </div>
            )}
        </div>
        <Snackbar open={snackbarOpen} autoHideDuration={6000} onClose={() => setSnackbarOpen(false)}>
            <Alert onClose={() => setSnackbarOpen(false)} severity="error" sx={{ width: '100%' }}>
                {snackbarMessage}
            </Alert>
        </Snackbar>
    </div>
);

};

export default TripForm;
