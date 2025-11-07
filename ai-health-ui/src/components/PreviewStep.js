import React, { useState } from 'react';
import {
  Box,
  Typography,
  Button,
  Paper,
  Alert,
  CircularProgress,
  Grid,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon
} from '@mui/material';
import {
  Refresh as RegenerateIcon,
  InsertDriveFile as FileIcon,
  Person as PersonIcon,
  Medication as MedicationIcon,
  LocalHospital as LocalHospitalIcon,
  CalendarToday as CalendarTodayIcon,
  NavigateNext as NextIcon,
  NavigateBefore as BackIcon
} from '@mui/icons-material';

const PreviewStep = ({ s3FileUrl, uploadedFile, onDataExtracted, onProceedToCarePlan, extractedData, onBack }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleRegenerate = async () => {
    setLoading(true);
    setError('');

    try {
      // Use different API base URL for development vs production
      const apiBaseUrl = process.env.NODE_ENV === 'development' ? 'http://localhost:8000' : '';
      
      const response = await fetch(`${apiBaseUrl}/upload/extract-medical-data`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          file_url: s3FileUrl,
          file_name: uploadedFile?.name || 'medical-document'
        }),
      });

      if (!response.ok) {
        throw new Error(`Extraction failed: ${response.status}`);
      }

      const responseData = await response.json();
      // Extract the data from the API response
      const extractedMedicalData = responseData.data || responseData;
      onDataExtracted(extractedMedicalData);
      
    } catch (error) {
      console.error('Extraction error:', error);
      setError(`Failed to extract data: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleNext = () => {
    if (extractedData) {
      // Navigate to next step - this will be handled by parent component
      // For now, we'll just show that we're ready
      console.log('Ready to proceed to care plan generation');
    }
  };

  const renderExtractedData = () => {
    if (!extractedData) return null;

    // Debug logging
    console.log('ExtractedData in renderExtractedData:', extractedData);

    const {
      patient_info = {},
      medications = [],
      medical_conditions = [],
      diagnosis = '',
      raw_text = '',
      clinical_notes = '',
      extracted_entities = []
    } = extractedData;

    return (
      <Box sx={{ mt: 3 }}>
        <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
          <LocalHospitalIcon sx={{ mr: 1 }} />
          Extracted Medical Data
        </Typography>

        <Grid container spacing={3}>
          {/* Patient Information */}
          {Object.keys(patient_info).length > 0 && (
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                    <PersonIcon sx={{ mr: 1 }} />
                    Patient Information
                  </Typography>
                  <List dense>
                    {patient_info.name && (
                      <ListItem>
                        <ListItemText primary="Name" secondary={patient_info.name} />
                      </ListItem>
                    )}
                    {patient_info.age && (
                      <ListItem>
                        <ListItemText primary="Age" secondary={patient_info.age} />
                      </ListItem>
                    )}
                    {patient_info.gender && (
                      <ListItem>
                        <ListItemText primary="Gender" secondary={patient_info.gender} />
                      </ListItem>
                    )}
                    {patient_info.weight && (
                      <ListItem>
                        <ListItemText primary="Weight" secondary={`${patient_info.weight} kg`} />
                      </ListItem>
                    )}
                  </List>
                </CardContent>
              </Card>
            </Grid>
          )}

          {/* Medications */}
          {medications.length > 0 && (
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                    <MedicationIcon sx={{ mr: 1 }} />
                    Medications ({medications.length})
                  </Typography>
                  <TableContainer>
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>Medication</TableCell>
                          <TableCell>Dosage</TableCell>
                          <TableCell>Duration</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {medications.map((med, index) => (
                          <TableRow key={index}>
                            <TableCell>{med.name || med.medication_name || 'N/A'}</TableCell>
                            <TableCell>{med.dosage || 'N/A'}</TableCell>
                            <TableCell>{med.duration || 'N/A'}</TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </CardContent>
              </Card>
            </Grid>
          )}

          {/* Medical Conditions */}
          {medical_conditions.length > 0 && (
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Medical Conditions
                  </Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                    {medical_conditions.map((condition, index) => (
                      <Chip
                        key={index}
                        label={condition}
                        variant="outlined"
                        color="secondary"
                      />
                    ))}
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          )}

          {/* Diagnosis */}
          {diagnosis && (
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Diagnosis
                  </Typography>
                  <Typography variant="body1">
                    {diagnosis}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          )}

          {/* Extracted Entities */}
          {extracted_entities.length > 0 && (
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Extracted Medical Entities
                  </Typography>
                  <TableContainer>
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>Type</TableCell>
                          <TableCell>Value</TableCell>
                          <TableCell>Confidence</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {extracted_entities.map((entity, index) => (
                          <TableRow key={index}>
                            <TableCell>
                              <Chip 
                                label={entity.type || entity.label} 
                                size="small" 
                                variant="outlined"
                              />
                            </TableCell>
                            <TableCell>{entity.text || entity.value}</TableCell>
                            <TableCell>
                              {entity.confidence && 
                                `${Math.round(entity.confidence * 100)}%`
                              }
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </CardContent>
              </Card>
            </Grid>
          )}

          {/* Raw Text Preview */}
          {(clinical_notes || raw_text) && (
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Document Text Preview
                  </Typography>
                  <Paper sx={{ p: 2, bgcolor: 'grey.50', maxHeight: 200, overflow: 'auto' }}>
                    <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                      {(clinical_notes || raw_text).substring(0, 1000)}
                      {(clinical_notes || raw_text).length > 1000 && '...'}
                    </Typography>
                  </Paper>
                </CardContent>
              </Card>
            </Grid>
          )}
        </Grid>
      </Box>
    );
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom sx={{ mb: 3 }}>
        Preview & Extract Medical Data
      </Typography>

      {/* File Info */}
      {uploadedFile && (
        <Paper sx={{ p: 3, mb: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <FileIcon sx={{ mr: 2, color: 'primary.main' }} />
              <Box>
                <Typography variant="h6">
                  {uploadedFile.name}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Uploaded successfully • Ready for data extraction
                </Typography>
              </Box>
            </Box>
            
            <Button
              variant="contained"
              onClick={handleRegenerate}
              disabled={loading}
              startIcon={loading ? <CircularProgress size={20} /> : <RegenerateIcon />}
            >
              {loading ? 'Extracting...' : extractedData ? 'Regenerate' : 'Extract Data'}
            </Button>
          </Box>
        </Paper>
      )}

      {/* Error Display */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Loading State */}
      {loading && (
        <Paper sx={{ p: 4, textAlign: 'center', mb: 3 }}>
          <CircularProgress size={40} sx={{ mb: 2 }} />
          <Typography variant="h6" gutterBottom>
            Extracting Medical Data...
          </Typography>
          <Typography variant="body2" color="textSecondary">
            Using AWS Textract and NER models to analyze your document
          </Typography>
        </Paper>
      )}

      {/* Extracted Data Display */}
      {renderExtractedData()}

      {/* Action Buttons */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4 }}>
        <Button
          variant="outlined"
          onClick={onBack}
          startIcon={<BackIcon />}
        >
          Back to Upload
        </Button>
        
        {extractedData && (
          <Button
            variant="contained"
            onClick={onProceedToCarePlan}
            endIcon={<NextIcon />}
            size="large"
          >
            Continue to Care Plan
          </Button>
        )}
      </Box>

      {/* Helpful Information */}
      {extractedData && (
        <Alert severity="info" sx={{ mt: 3 }}>
          <Typography variant="body2">
            💡 <strong>Next Step:</strong> The extracted medical data will be used to pre-fill the care plan generation form. 
            You can review and modify the information before generating your personalized care plan.
          </Typography>
        </Alert>
      )}
    </Box>
  );
};

export default PreviewStep;