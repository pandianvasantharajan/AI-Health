import React, { useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Chip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Alert,
  Paper,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  Assignment as AssignmentIcon,
  LocalPharmacy as PharmacyIcon,
  FitnessCenter as FitnessIcon,
  Schedule as ScheduleIcon,
  Info as InfoIcon,
  CheckCircle as CheckIcon,
  Warning as WarningIcon,
  Person as PersonIcon,
  Speed as SpeedIcon,
  Psychology as PsychologyIcon,
  Print as PrintIcon,
} from '@mui/icons-material';

const CarePlanResult = ({ carePlan }) => {
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedSection, setSelectedSection] = useState(null);

  if (!carePlan || !carePlan.care_plan) {
    return (
      <Alert severity="info">
        No care plan data available
      </Alert>
    );
  }

  const { care_plan, model_used, model_type, diagnosis } = carePlan;

  const handleViewDetails = (section) => {
    setSelectedSection(section);
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setSelectedSection(null);
  };

  const handlePrint = () => {
    window.print();
  };

  const getSectionIcon = (sectionType) => {
    switch (sectionType) {
      case 'treatment_plan':
        return <AssignmentIcon color="primary" />;
      case 'medication_management':
        return <PharmacyIcon color="secondary" />;
      case 'lifestyle_recommendations':
        return <FitnessIcon color="success" />;
      case 'follow_up_recommendations':
        return <ScheduleIcon color="warning" />;
      default:
        return <InfoIcon color="info" />;
    }
  };

  const renderSection = (section, title, icon) => {
    if (!section || section.length === 0) return null;

    return (
      <Card sx={{ mb: 2, elevation: 2 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            {icon}
            <Typography variant="h6" sx={{ ml: 1, color: 'primary.main', fontWeight: 600 }}>
              {title}
            </Typography>
          </Box>
          
          {section.map((item, index) => (
            <Accordion key={index} sx={{ mb: 1, '&:before': { display: 'none' } }}>
              <AccordionSummary
                expandIcon={<ExpandMoreIcon />}
                sx={{
                  backgroundColor: 'grey.50',
                  '&:hover': { backgroundColor: 'grey.100' },
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                  <Typography variant="subtitle1" sx={{ fontWeight: 500, flexGrow: 1 }}>
                    {item.title}
                  </Typography>
                  {item.priority && (
                    <Chip
                      label={item.priority}
                      size="small"
                      color={
                        item.priority === 'high' ? 'error' :
                        item.priority === 'medium' ? 'warning' : 'success'
                      }
                      sx={{ ml: 2 }}
                    />
                  )}
                </Box>
              </AccordionSummary>
              <AccordionDetails sx={{ pt: 2 }}>
                <Typography variant="body1" sx={{ lineHeight: 1.6 }}>
                  {item.content}
                </Typography>
                {item.details && (
                  <Button
                    variant="outlined"
                    size="small"
                    onClick={() => handleViewDetails(item)}
                    sx={{ mt: 2 }}
                  >
                    View Details
                  </Button>
                )}
              </AccordionDetails>
            </Accordion>
          ))}
        </CardContent>
      </Card>
    );
  };

  return (
    <Box>
      {/* Header Section */}
      <Paper elevation={3} sx={{ p: 3, mb: 3, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
        <Grid container spacing={3} alignItems="center">
          <Grid item xs={12} md={8}>
            <Typography variant="h5" sx={{ fontWeight: 600, mb: 1 }}>
              AI-Generated Care Plan
            </Typography>
            <Typography variant="body1" sx={{ opacity: 0.9, mb: 2 }}>
              <strong>Diagnosis:</strong> {diagnosis}
            </Typography>
            {care_plan.summary && (
              <Typography variant="body2" sx={{ opacity: 0.8 }}>
                {care_plan.summary}
              </Typography>
            )}
          </Grid>
          <Grid item xs={12} md={4}>
            <Box sx={{ textAlign: { xs: 'left', md: 'right' } }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1, justifyContent: { xs: 'flex-start', md: 'flex-end' } }}>
                <PsychologyIcon sx={{ mr: 1 }} />
                <Typography variant="body2">
                  <strong>{model_type}</strong>
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2, justifyContent: { xs: 'flex-start', md: 'flex-end' } }}>
                <SpeedIcon sx={{ mr: 1 }} />
                <Typography variant="caption">
                  Model: {model_used}
                </Typography>
              </Box>
              <Button
                variant="contained"
                startIcon={<PrintIcon />}
                onClick={handlePrint}
                sx={{ 
                  bgcolor: 'rgba(255,255,255,0.2)', 
                  '&:hover': { bgcolor: 'rgba(255,255,255,0.3)' }
                }}
              >
                Print Care Plan
              </Button>
            </Box>
          </Grid>
        </Grid>
      </Paper>

      {/* Care Plan Sections */}
      <Grid container spacing={3}>
        <Grid item xs={12}>
          {renderSection(
            care_plan.treatment_plan,
            'Treatment Plan',
            <AssignmentIcon color="primary" />
          )}
        </Grid>
        
        <Grid item xs={12}>
          {renderSection(
            care_plan.medication_management,
            'Medication Management',
            <PharmacyIcon color="secondary" />
          )}
        </Grid>
        
        <Grid item xs={12}>
          {renderSection(
            care_plan.lifestyle_recommendations,
            'Lifestyle Recommendations',
            <FitnessIcon color="success" />
          )}
        </Grid>
        
        <Grid item xs={12}>
          {renderSection(
            care_plan.follow_up_recommendations,
            'Follow-up Recommendations',
            <ScheduleIcon color="warning" />
          )}
        </Grid>
      </Grid>

      {/* Model Performance Indicator */}
      <Paper elevation={1} sx={{ p: 2, mt: 3, bgcolor: 'success.light', color: 'success.contrastText' }}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <CheckIcon sx={{ mr: 1 }} />
          <Typography variant="body2">
            <strong>Care Plan Generated Successfully</strong> • 
            Medical factors analyzed with Amazon Nova Micro • 
            Comprehensive assessment complete
          </Typography>
        </Box>
      </Paper>

      {/* Detailed View Dialog */}
      <Dialog
        open={openDialog}
        onClose={handleCloseDialog}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <InfoIcon sx={{ mr: 1, color: 'primary.main' }} />
            {selectedSection?.title}
          </Box>
        </DialogTitle>
        <DialogContent>
          <Typography variant="body1" sx={{ mb: 2, lineHeight: 1.6 }}>
            {selectedSection?.content}
          </Typography>
          
          {selectedSection?.details && (
            <Box>
              <Divider sx={{ my: 2 }} />
              <Typography variant="h6" sx={{ mb: 2, color: 'primary.main' }}>
                Additional Details
              </Typography>
              <Typography variant="body2" sx={{ lineHeight: 1.6 }}>
                {selectedSection.details}
              </Typography>
            </Box>
          )}
          
          {selectedSection?.priority && (
            <Box sx={{ mt: 2 }}>
              <Chip
                label={`Priority: ${selectedSection.priority}`}
                color={
                  selectedSection.priority === 'high' ? 'error' :
                  selectedSection.priority === 'medium' ? 'warning' : 'success'
                }
              />
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog} color="primary">
            Close
          </Button>
        </DialogActions>
      </Dialog>

      {/* Medical Factors Analysis Footer */}
      <Box sx={{ mt: 4, p: 2, bgcolor: 'background.paper', borderRadius: 2, border: '1px solid', borderColor: 'divider' }}>
        <Typography variant="caption" color="textSecondary" sx={{ display: 'block', textAlign: 'center' }}>
          💡 This care plan was generated using advanced AI medical factor analysis. 
          Always consult with healthcare professionals for medical decisions.
        </Typography>
      </Box>
    </Box>
  );
};

export default CarePlanResult;