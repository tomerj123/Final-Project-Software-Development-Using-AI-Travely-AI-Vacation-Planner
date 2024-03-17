// frontend/src/components/TripPlan.js

import React from 'react';

const TripPlan = ({ plan }) => {
  return (
    <div>
      <h2>Your Trip Plan</h2>
      {/* Display the trip plan as HTML */}
      <div dangerouslySetInnerHTML={{ __html: plan }} />
    </div>
  );
};

export default TripPlan;
