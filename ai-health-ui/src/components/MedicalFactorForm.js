import React, { useState } from 'react';
import {
  Grid,
  TextField,
  Button,
  Box,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  IconButton,
  Divider,
  Card,
  CardContent,
  CircularProgress,
  InputAdornment,
  Menu,
  ListItemText,
  ListItemIcon,
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Person as PersonIcon,
  LocalHospital as HospitalIcon,
  Medication as MedicationIcon,
  Notes as NotesIcon,
  AutoFixHigh as SampleIcon,
} from '@mui/icons-material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';

const MedicalFactorForm = ({ onSubmit, loading, onClearCarePlan }) => {
  const [formData, setFormData] = useState({
    patient_info: {
      age: '',
      gender: '',
      weight: '',
      medical_conditions: [],
      allergies: [],
    },
    diagnosis: '',
    prescriptions: [
      {
        medication_name: '',
        dosage: '',
        duration: '',
        instructions: '',
      },
    ],
    doctor_notes: '',
    prescription_date: new Date(),
  });

  const [newCondition, setNewCondition] = useState('');
  const [newAllergy, setNewAllergy] = useState('');
  const [sampleMenuAnchor, setSampleMenuAnchor] = useState(null);

  // Sample patient data for prefilling
  const sampleCases = {
    heartFailure: {
      name: 'Heart Failure Case',
      description: 'Complex heart failure with multiple comorbidities',
      data: {
        patient_info: {
          age: '65',
          gender: 'Female',
          weight: '68.0',
          medical_conditions: ['Hypertension', 'Type 2 Diabetes', 'Chronic Kidney Disease Stage 3'],
          allergies: ['Penicillin', 'Iodine contrast'],
        },
        diagnosis: 'Acute exacerbation of chronic heart failure with reduced ejection fraction',
        prescriptions: [
          {
            medication_name: 'Furosemide',
            dosage: '40mg twice daily',
            duration: '14 days, then reassess',
            instructions: 'Take with food. Monitor weight daily. Report weight gain >2lbs in 24hrs',
          },
          {
            medication_name: 'Metoprolol succinate',
            dosage: '25mg daily',
            duration: 'Ongoing',
            instructions: 'Take with or without food. Do not stop abruptly. Check pulse before taking',
          },
          {
            medication_name: 'Lisinopril',
            dosage: '5mg daily',
            duration: 'Ongoing',
            instructions: 'Take at same time daily. Avoid potassium supplements. Monitor kidney function',
          },
        ],
        doctor_notes: 'Patient presents with dyspnea, peripheral edema, and weight gain. Chest X-ray shows pulmonary edema. BNP elevated at 850. Creatinine 1.8 (baseline 1.5). Careful fluid balance management needed. Follow up in 1 week for weight and symptoms. Cardiology referral if no improvement.',
        prescription_date: new Date(),
      }
    },
    asthma: {
      name: 'Asthma Exacerbation',
      description: 'Young adult with acute asthma attack',
      data: {
        patient_info: {
          age: '28',
          gender: 'Male',
          weight: '75.0',
          medical_conditions: ['Asthma', 'Seasonal Allergies'],
          allergies: ['Sulfa drugs', 'Tree pollen'],
        },
        diagnosis: 'Acute asthma exacerbation with bronchospasm',
        prescriptions: [
          {
            medication_name: 'Prednisone',
            dosage: '40mg daily for 5 days',
            duration: '5 days',
            instructions: 'Take with food to reduce stomach irritation. Complete full course',
          },
          {
            medication_name: 'Albuterol inhaler',
            dosage: '2 puffs every 4-6 hours as needed',
            duration: '30 days',
            instructions: 'Shake well before use. Rinse mouth after use',
          },
        ],
        doctor_notes: 'Patient experiencing wheezing and shortness of breath. Peak flow reduced to 60% of baseline. Started on oral corticosteroids and bronchodilator. Follow up in 3-5 days or sooner if symptoms worsen.',
        prescription_date: new Date(),
      }
    },
    diabetes: {
      name: 'Diabetes Management',
      description: 'Elderly patient with diabetes complications',
      data: {
        patient_info: {
          age: '72',
          gender: 'Male',
          weight: '82.0',
          medical_conditions: ['Type 2 Diabetes', 'Diabetic Neuropathy', 'Hypertension', 'High cholesterol'],
          allergies: ['NKDA'],
        },
        diagnosis: 'Uncontrolled Type 2 Diabetes with peripheral neuropathy',
        prescriptions: [
          {
            medication_name: 'Metformin',
            dosage: '1000mg twice daily',
            duration: 'Ongoing',
            instructions: 'Take with meals to reduce GI upset. Monitor kidney function',
          },
          {
            medication_name: 'Insulin glargine',
            dosage: '20 units subcutaneous at bedtime',
            duration: 'Ongoing',
            instructions: 'Rotate injection sites. Monitor blood glucose levels',
          },
          {
            medication_name: 'Gabapentin',
            dosage: '300mg three times daily',
            duration: 'Ongoing',
            instructions: 'For neuropathic pain. May cause drowsiness',
          },
        ],
        doctor_notes: 'HbA1c elevated at 9.2%. Patient reports numbness and tingling in feet. Started on gabapentin for neuropathy. Diabetes education referral. Follow up in 4 weeks for glucose monitoring and medication adjustment.',
        prescription_date: new Date(),
      }
    }
  };

  const loadSampleData = (caseType = 'heartFailure') => {
    setFormData(sampleCases[caseType].data);
    setSampleMenuAnchor(null);
  };

  const handleSampleMenuOpen = (event) => {
    setSampleMenuAnchor(event.currentTarget);
  };

  const handleSampleMenuClose = () => {
    setSampleMenuAnchor(null);
  };

  const clearForm = () => {
    setFormData({
      patient_info: {
        age: '',
        gender: '',
        weight: '',
        medical_conditions: [],
        allergies: [],
      },
      diagnosis: '',
      prescriptions: [
        {
          medication_name: '',
          dosage: '',
          duration: '',
          instructions: '',
        },
      ],
      doctor_notes: '',
      prescription_date: new Date(),
    });
    setNewCondition('');
    setNewAllergy('');
    // Clear the generated care plan as well
    if (onClearCarePlan) {
      onClearCarePlan();
    }
  };

  const handleInputChange = (field, value, section = null, index = null) => {
    if (section && index !== null) {
      // Handle nested array updates (prescriptions)
      setFormData(prev => ({
        ...prev,
        [section]: prev[section].map((item, i) => 
          i === index ? { ...item, [field]: value } : item
        ),
      }));
    } else if (section) {
      // Handle nested object updates (patient_info)
      setFormData(prev => ({
        ...prev,
        [section]: {
          ...prev[section],
          [field]: value,
        },
      }));
    } else {
      // Handle top-level updates
      setFormData(prev => ({
        ...prev,
        [field]: value,
      }));
    }
  };

  const addMedicalCondition = () => {
    if (newCondition.trim()) {
      setFormData(prev => ({
        ...prev,
        patient_info: {
          ...prev.patient_info,
          medical_conditions: [...prev.patient_info.medical_conditions, newCondition.trim()],
        },
      }));
      setNewCondition('');
    }
  };

  const removeMedicalCondition = (index) => {
    setFormData(prev => ({
      ...prev,
      patient_info: {
        ...prev.patient_info,
        medical_conditions: prev.patient_info.medical_conditions.filter((_, i) => i !== index),
      },
    }));
  };

  const addAllergy = () => {
    if (newAllergy.trim()) {
      setFormData(prev => ({
        ...prev,
        patient_info: {
          ...prev.patient_info,
          allergies: [...prev.patient_info.allergies, newAllergy.trim()],
        },
      }));
      setNewAllergy('');
    }
  };

  const removeAllergy = (index) => {
    setFormData(prev => ({
      ...prev,
      patient_info: {
        ...prev.patient_info,
        allergies: prev.patient_info.allergies.filter((_, i) => i !== index),
      },
    }));
  };

  const addPrescription = () => {
    setFormData(prev => ({
      ...prev,
      prescriptions: [
        ...prev.prescriptions,
        {
          medication_name: '',
          dosage: '',
          duration: '',
          instructions: '',
        },
      ],
    }));
  };

  const removePrescription = (index) => {
    if (formData.prescriptions.length > 1) {
      setFormData(prev => ({
        ...prev,
        prescriptions: prev.prescriptions.filter((_, i) => i !== index),
      }));
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Convert form data to the required format
    const submissionData = {
      ...formData,
      patient_info: {
        ...formData.patient_info,
        age: parseInt(formData.patient_info.age) || 0,
        weight: parseFloat(formData.patient_info.weight) || 0,
      },
      prescription_date: formData.prescription_date.toISOString().split('T')[0],
    };
    
    onSubmit(submissionData);
  };

  const isFormValid = () => {
    return (
      formData.patient_info.age &&
      formData.patient_info.gender &&
      formData.diagnosis &&
      formData.prescriptions[0].medication_name
    );
  };

  return (
    <Box component="form" onSubmit={handleSubmit}>
      {/* Sample Data Controls */}
      <Card sx={{ mb: 3, bgcolor: 'primary.light', color: 'primary.contrastText' }}>
        <CardContent sx={{ py: 2 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 2 }}>
            <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center' }}>
              <SampleIcon sx={{ mr: 1 }} />
              Quick Start Options
            </Typography>
            <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
              <Button
                variant="contained"
                color="secondary"
                onClick={handleSampleMenuOpen}
                startIcon={<SampleIcon />}
                sx={{ 
                  bgcolor: 'secondary.main',
                  '&:hover': { bgcolor: 'secondary.dark' }
                }}
              >
                Load Sample Cases
              </Button>
              <Menu
                anchorEl={sampleMenuAnchor}
                open={Boolean(sampleMenuAnchor)}
                onClose={handleSampleMenuClose}
                PaperProps={{
                  sx: { minWidth: 300 }
                }}
              >
                {Object.entries(sampleCases).map(([key, caseData]) => (
                  <MenuItem key={key} onClick={() => loadSampleData(key)}>
                    <ListItemIcon>
                      <HospitalIcon color="primary" />
                    </ListItemIcon>
                    <ListItemText
                      primary={caseData.name}
                      secondary={caseData.description}
                    />
                  </MenuItem>
                ))}
              </Menu>
              <Button
                variant="outlined"
                onClick={clearForm}
                sx={{ 
                  color: 'primary.contrastText',
                  borderColor: 'primary.contrastText',
                  '&:hover': { 
                    bgcolor: 'rgba(255,255,255,0.1)',
                    borderColor: 'primary.contrastText'
                  }
                }}
              >
                Clear All Fields
              </Button>
            </Box>
          </Box>
          <Typography variant="body2" sx={{ mt: 1, opacity: 0.9 }}>
            💡 Choose from sample medical cases: Heart Failure, Asthma, or Diabetes - or start with a clean form
          </Typography>
        </CardContent>
      </Card>

      {/* Patient Information Section */}
      <Card className="form-section" sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" className="form-section-title" sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <PersonIcon sx={{ mr: 1 }} />
            Patient Information
          </Typography>
          
          <Grid container spacing={3}>
            <Grid item xs={12} sm={6} md={3}>
              <TextField
                fullWidth
                label="Age"
                type="number"
                value={formData.patient_info.age}
                onChange={(e) => handleInputChange('age', e.target.value, 'patient_info')}
                required
                inputProps={{ min: 0, max: 120 }}
              />
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth required>
                <InputLabel>Gender</InputLabel>
                <Select
                  value={formData.patient_info.gender}
                  onChange={(e) => handleInputChange('gender', e.target.value, 'patient_info')}
                  label="Gender"
                >
                  <MenuItem value="Male">Male</MenuItem>
                  <MenuItem value="Female">Female</MenuItem>
                  <MenuItem value="Other">Other</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <TextField
                fullWidth
                label="Weight (kg)"
                type="number"
                value={formData.patient_info.weight}
                onChange={(e) => handleInputChange('weight', e.target.value, 'patient_info')}
                inputProps={{ min: 0, step: 0.1 }}
                InputProps={{
                  endAdornment: <InputAdornment position="end">kg</InputAdornment>,
                }}
              />
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <DatePicker
                label="Prescription Date"
                value={formData.prescription_date}
                onChange={(date) => handleInputChange('prescription_date', date)}
                renderInput={(params) => <TextField {...params} fullWidth />}
              />
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Medical Conditions Section */}
      <Card className="form-section" sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" className="form-section-title" sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <HospitalIcon sx={{ mr: 1 }} />
            Medical Conditions
          </Typography>
          
          <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
            <TextField
              fullWidth
              label="Add Medical Condition"
              value={newCondition}
              onChange={(e) => setNewCondition(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addMedicalCondition())}
            />
            <Button
              variant="contained"
              onClick={addMedicalCondition}
              disabled={!newCondition.trim()}
              sx={{ minWidth: 'auto', px: 2 }}
            >
              <AddIcon />
            </Button>
          </Box>
          
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {formData.patient_info.medical_conditions.map((condition, index) => (
              <Chip
                key={index}
                label={condition}
                onDelete={() => removeMedicalCondition(index)}
                color="primary"
                variant="outlined"
                className="medical-conditions-chip"
              />
            ))}
          </Box>
        </CardContent>
      </Card>

      {/* Allergies Section */}
      <Card className="form-section" sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" className="form-section-title" sx={{ mb: 2 }}>
            ⚠️ Allergies
          </Typography>
          
          <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
            <TextField
              fullWidth
              label="Add Allergy"
              value={newAllergy}
              onChange={(e) => setNewAllergy(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addAllergy())}
            />
            <Button
              variant="contained"
              color="warning"
              onClick={addAllergy}
              disabled={!newAllergy.trim()}
              sx={{ minWidth: 'auto', px: 2 }}
            >
              <AddIcon />
            </Button>
          </Box>
          
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {formData.patient_info.allergies.map((allergy, index) => (
              <Chip
                key={index}
                label={allergy}
                onDelete={() => removeAllergy(index)}
                color="warning"
                variant="outlined"
                className="allergies-chip"
              />
            ))}
          </Box>
        </CardContent>
      </Card>

      {/* Diagnosis Section */}
      <Card className="form-section" sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" className="form-section-title" sx={{ mb: 2 }}>
            🔍 Diagnosis
          </Typography>
          
          <TextField
            fullWidth
            label="Primary Diagnosis"
            value={formData.diagnosis}
            onChange={(e) => handleInputChange('diagnosis', e.target.value)}
            required
            multiline
            rows={2}
            placeholder="Enter the primary diagnosis for this patient..."
          />
        </CardContent>
      </Card>

      {/* Prescriptions Section */}
      <Card className="form-section" sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" className="form-section-title" sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <MedicationIcon sx={{ mr: 1 }} />
            Prescriptions
          </Typography>
          
          {formData.prescriptions.map((prescription, index) => (
            <Card key={index} className="prescription-item" sx={{ mb: 2, bgcolor: 'background.default' }}>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="subtitle1" color="primary">
                    Medication #{index + 1}
                  </Typography>
                  {formData.prescriptions.length > 1 && (
                    <IconButton
                      color="error"
                      onClick={() => removePrescription(index)}
                      size="small"
                    >
                      <DeleteIcon />
                    </IconButton>
                  )}
                </Box>
                
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Medication Name"
                      value={prescription.medication_name}
                      onChange={(e) => handleInputChange('medication_name', e.target.value, 'prescriptions', index)}
                      required={index === 0}
                    />
                  </Grid>
                  
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Dosage"
                      value={prescription.dosage}
                      onChange={(e) => handleInputChange('dosage', e.target.value, 'prescriptions', index)}
                      placeholder="e.g., 500mg twice daily"
                    />
                  </Grid>
                  
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Duration"
                      value={prescription.duration}
                      onChange={(e) => handleInputChange('duration', e.target.value, 'prescriptions', index)}
                      placeholder="e.g., 7 days"
                    />
                  </Grid>
                  
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Instructions"
                      value={prescription.instructions}
                      onChange={(e) => handleInputChange('instructions', e.target.value, 'prescriptions', index)}
                      placeholder="e.g., Take with food"
                    />
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          ))}
          
          <Button
            variant="outlined"
            onClick={addPrescription}
            startIcon={<AddIcon />}
            sx={{ mt: 1 }}
          >
            Add Another Prescription
          </Button>
        </CardContent>
      </Card>

      {/* Doctor Notes Section */}
      <Card className="form-section" sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" className="form-section-title" sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <NotesIcon sx={{ mr: 1 }} />
            Doctor Notes
          </Typography>
          
          <TextField
            fullWidth
            label="Additional Notes"
            value={formData.doctor_notes}
            onChange={(e) => handleInputChange('doctor_notes', e.target.value)}
            multiline
            rows={4}
            placeholder="Enter any additional notes, observations, or special instructions..."
          />
        </CardContent>
      </Card>

      {/* Submit Button */}
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <Button
          type="submit"
          variant="contained"
          size="large"
          disabled={!isFormValid() || loading}
          sx={{ 
            minWidth: 200, 
            height: 50,
            fontSize: '1.1rem',
            fontWeight: 600,
          }}
        >
          {loading ? (
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <CircularProgress size={24} sx={{ mr: 1 }} />
              Generating Care Plan...
            </Box>
          ) : (
            '🚀 Generate Care Plan with Nova Micro'
          )}
        </Button>
      </Box>
    </Box>
  );
};

export default MedicalFactorForm;