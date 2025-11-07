import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Paper,
  Alert,
  Grid
} from '@mui/material';
import {
  NavigateBefore as BackIcon,
  AutoAwesome as GenerateIcon
} from '@mui/icons-material';
import MedicalFactorForm from './MedicalFactorForm';
import CarePlanResult from './CarePlanResult';

const NewCarePlanStep = ({ extractedData, onCarePlanGenerated, carePlan, onBack }) => {
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [preFilledData, setPreFilledData] = useState(null);

  useEffect(() => {
    if (extractedData) {
      // Transform extracted data to match MedicalFactorForm structure
      const transformedData = transformExtractedData(extractedData);
      setPreFilledData(transformedData);
    }
  }, [extractedData]);

  const transformExtractedData = (data) => {
    console.log('Transforming extracted data:', data);
    
    const {
      patient_info = {},
      medications = [],
      medical_conditions = [],
      diagnosis = '',
      clinical_notes = '',
      allergies = []
    } = data;

    // Ensure we have at least one prescription entry for form validation
    let prescriptions = medications.length > 0 
      ? medications.map(med => ({
          medication_name: med.name || med.medication_name || '',
          dosage: med.dosage || '',
          duration: med.duration || '',
          instructions: med.instructions || '',
        }))
      : [
          {
            medication_name: 'No medications extracted',
            dosage: '',
            duration: '',
            instructions: 'Please update with actual medications if needed',
          }
        ];

    // Ensure at least the first prescription has a medication name for validation
    if (prescriptions.length > 0 && !prescriptions[0].medication_name) {
      prescriptions[0].medication_name = 'Review required - update medication information';
    }

    // Transform to match the expected form structure
    const formData = {
      patient_info: {
        age: patient_info.age || '',
        gender: patient_info.gender || 'Unknown', // Set default to prevent validation failure
        weight: patient_info.weight || '',
        medical_conditions: medical_conditions || [],
        allergies: allergies || [],
      },
      diagnosis: diagnosis || clinical_notes || 'Medical document analysis',
      prescriptions: prescriptions,
      prescription_date: new Date(),
      symptoms: data.symptoms || [],
      medical_history: data.medical_history || '',
      lifestyle_factors: {
        smoking: data.lifestyle_factors?.smoking || '',
        alcohol_consumption: data.lifestyle_factors?.alcohol_consumption || '',
        exercise_frequency: data.lifestyle_factors?.exercise_frequency || '',
        diet_preferences: data.lifestyle_factors?.diet_preferences || '',
      }
    };

    console.log('Transformed form data:', formData);
    return formData;
  };

  const handleCarePlanGenerated = (planData) => {
    setError('');
    onCarePlanGenerated(planData);
  };

  const handleError = (errorMessage) => {
    setError(errorMessage);
  };

  const handleLoading = (isLoading) => {
    setLoading(isLoading);
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom sx={{ mb: 3 }}>
        Generate New Care Plan
      </Typography>

      {/* Information Alert */}
      <Alert severity="info" sx={{ mb: 3 }}>
        <Typography variant="body2">
          📋 <strong>Pre-filled Data:</strong> The form below has been automatically populated with information 
          extracted from your uploaded document. Please review and modify any details as needed before generating your care plan.
        </Typography>
      </Alert>

      <Grid container spacing={3}>
        {/* Medical Factor Form */}
        <Grid item xs={12}>
          <Paper elevation={3} sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom sx={{ mb: 3 }}>
              Medical Information Review
            </Typography>
            
            {preFilledData ? (
              <MedicalFactorForm
                onCarePlanGenerated={handleCarePlanGenerated}
                onError={handleError}
                onLoading={handleLoading}
                initialData={preFilledData}
                showTitle={false}
              />
            ) : (
              <Typography variant="body1" color="textSecondary">
                Loading extracted medical data...
              </Typography>
            )}
          </Paper>
        </Grid>

        {/* Error Display */}
        {error && (
          <Grid item xs={12}>
            <Alert severity="error">
              {error}
            </Alert>
          </Grid>
        )}

        {/* Care Plan Results */}
        {carePlan && (
          <Grid item xs={12}>
            <Paper elevation={3} sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom sx={{ mb: 3, color: 'success.main' }}>
                🎉 Generated Care Plan
              </Typography>
              <CarePlanResult carePlan={carePlan} />
            </Paper>
          </Grid>
        )}
      </Grid>

      {/* Navigation Buttons */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4 }}>
        <Button
          variant="outlined"
          onClick={onBack}
          startIcon={<BackIcon />}
        >
          Back to Preview
        </Button>
        
        {carePlan && (
          <Alert severity="success" sx={{ display: 'flex', alignItems: 'center' }}>
            <Typography variant="body2">
              ✅ Care plan generated successfully! You can now review the complete analysis.
            </Typography>
          </Alert>
        )}
      </Box>

      {/* Instructions */}
      {!carePlan && (
        <Paper sx={{ p: 3, mt: 3, bgcolor: 'grey.50' }}>
          <Typography variant="h6" gutterBottom>
            Instructions
          </Typography>
          <Typography variant="body2" paragraph>
            1. <strong>Review Pre-filled Data:</strong> Check that all extracted information is accurate
          </Typography>
          <Typography variant="body2" paragraph>
            2. <strong>Add Missing Information:</strong> Fill in any missing patient details, symptoms, or medical history
          </Typography>
          <Typography variant="body2" paragraph>
            3. <strong>Verify Medications:</strong> Ensure all prescriptions are correctly listed with proper dosages
          </Typography>
          <Typography variant="body2">
            4. <strong>Generate Care Plan:</strong> Click the "Submit" button to create your personalized care plan using AI analysis
          </Typography>
        </Paper>
      )}
    </Box>
  );
};

export default NewCarePlanStep;