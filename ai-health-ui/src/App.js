import React, { useState } from 'react';
import {
  Container,
  Paper,
  Typography,
  Box,
  AppBar,
  Toolbar,
  Alert,
  Snackbar,
} from '@mui/material';
import MedicalFactorForm from './components/MedicalFactorForm';
import CarePlanResult from './components/CarePlanResult';
import './App.css';

function App() {
  const [carePlan, setCarePlan] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const handleFormSubmit = async (medicalData) => {
    setLoading(true);
    setError(null);
    setCarePlan(null);
    
    try {
      // Use different API base URL for development vs production
      const apiBaseUrl = process.env.NODE_ENV === 'development' ? 'http://localhost:8000' : '';
      const response = await fetch(`${apiBaseUrl}/care-plan/nova-micro`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(medicalData),
      });

      const data = await response.json();
      
      if (data.success) {
        setCarePlan(data);
        setSuccess(true);
      } else {
        setError(data.detail || 'Failed to generate care plan');
      }
    } catch (err) {
      setError('Network error: Unable to connect to the AI Health Service');
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCloseSnackbar = () => {
    setError(null);
    setSuccess(false);
  };

  return (
    <Box sx={{ flexGrow: 1 }}>
      {/* App Bar */}
      <AppBar position="static" elevation={2}>
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            🏥 HUMAN-AI-HEALTH
          </Typography>
          <Typography variant="body2" sx={{ opacity: 0.8 }}>
          </Typography>
        </Toolbar>
      </AppBar>

        {/* Main Content */}
        <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
          <Box sx={{ mb: 3 }}>
            <Typography variant="h4" gutterBottom align="left" color="primary">
              Medical Factor Analysis & Care Plan Generation
            </Typography>

          </Box>

          {/* Medical Factor Form */}
          <Paper elevation={3} sx={{ p: 3, mb: 4 }}>
            <Typography variant="h6" gutterBottom color="primary">
              📋 Patient Medical Information
            </Typography>
            <MedicalFactorForm 
              onSubmit={handleFormSubmit} 
              loading={loading} 
              onClearCarePlan={() => setCarePlan(null)}
            />
          </Paper>

          {/* Care Plan Results */}
          {carePlan && (
            <Paper elevation={3} sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom color="primary">
                🎯 Generated Care Plan
              </Typography>
              <CarePlanResult carePlan={carePlan} />
            </Paper>
          )}

          {/* Success/Error Notifications */}
          <Snackbar
            open={!!error}
            autoHideDuration={6000}
            onClose={handleCloseSnackbar}
            anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
          >
            <Alert onClose={handleCloseSnackbar} severity="error" sx={{ width: '100%' }}>
              {error}
            </Alert>
          </Snackbar>

          <Snackbar
            open={success}
            autoHideDuration={4000}
            onClose={handleCloseSnackbar}
            anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
          >
            <Alert onClose={handleCloseSnackbar} severity="success" sx={{ width: '100%' }}>
              Care plan generated successfully! 🎉
            </Alert>
          </Snackbar>
        </Container>

        {/* Footer */}
        <Box 
          component="footer" 
          sx={{ 
            mt: 'auto', 
            py: 2, 
            px: 2, 
            backgroundColor: 'background.paper',
            borderTop: '1px solid',
            borderColor: 'divider'
          }}
        >
          <Container maxWidth="lg">
            <Typography variant="body2" color="textSecondary" align="center">
              AI Health Service © 2025 | Medical Factor Analysis with Amazon Nova Micro
            </Typography>
          </Container>
        </Box>
      </Box>
  );
}

export default App;