import React, { useState } from 'react';
import { Box, Typography, Paper, Alert } from '@mui/material';
import MedicalFactorForm from './MedicalFactorForm';
import CarePlanResult from './CarePlanResult';

const CarePlan = () => {
  const [carePlan, setCarePlan] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleCarePlanGenerated = (planData) => {
    setCarePlan(planData);
    setError('');
  };

  const handleError = (errorMessage) => {
    setError(errorMessage);
    setCarePlan(null);
  };

  const handleLoading = (isLoading) => {
    setLoading(isLoading);
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" gutterBottom align="left" color="primary">
          Medical Factor Analysis & Care Plan Generation
        </Typography>
      </Box>

      {/* Medical Factor Form */}
      <Paper elevation={3} sx={{ p: 3, mb: 4 }}>
        <MedicalFactorForm
          onCarePlanGenerated={handleCarePlanGenerated}
          onError={handleError}
          onLoading={handleLoading}
        />
      </Paper>

      {/* Error Display */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Care Plan Results */}
      {carePlan && (
        <Paper elevation={3} sx={{ p: 3 }}>
          <CarePlanResult carePlan={carePlan} />
        </Paper>
      )}
    </Box>
  );
};

export default CarePlan;