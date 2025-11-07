import React, { useState, useEffect } from 'react';
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
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
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

  // Debug function to log the carePlan data structure
  const debugCarePlanData = () => {
    console.log('CarePlan Data Structure:', carePlan);
    if (carePlan?.medical_data?.prescriptions) {
      console.log('Prescriptions:', carePlan.medical_data.prescriptions);
    }
  };

  // Clean and validate medication data
  const cleanMedicationData = (prescriptions) => {
    if (!prescriptions || !Array.isArray(prescriptions)) {
      return [];
    }

    return prescriptions
      .filter(prescription => {
        // Basic validation
        if (!prescription || typeof prescription !== 'object') {
          return false;
        }

        const medicationName = prescription.medication_name;
        
        // Check if medication name exists and is valid
        if (!medicationName || typeof medicationName !== 'string') {
          return false;
        }

        const cleanName = medicationName.trim().toLowerCase();
        
        // Filter out invalid entries
        const invalidPatterns = [
          'hi sam',
          'session',
          'working professional',
          'weekend',
          'office work',
          'study',
          'personally',
          '@',
          'great if you',
          'tight on',
          'coming weekend'
        ];

        // Check if medication name contains invalid patterns
        const hasInvalidPattern = invalidPatterns.some(pattern => 
          cleanName.includes(pattern)
        );

        if (hasInvalidPattern) {
          console.warn('Filtered out invalid medication entry:', medicationName);
          return false;
        }

        // Check if it's a reasonable medication name (not too long, not too short)
        if (cleanName.length < 2 || cleanName.length > 50) {
          return false;
        }

        // Check if it contains too many words (likely not a medication)
        if (cleanName.split(' ').length > 5) {
          return false;
        }

        return true;
      })
      .map(prescription => ({
        ...prescription,
        medication_name: prescription.medication_name.trim(),
        dosage: prescription.dosage?.trim() || '',
        duration: prescription.duration?.trim() || '',
        instructions: prescription.instructions?.trim() || '',
        schedule: {
          frequency: prescription.schedule?.frequency || '',
          times: Array.isArray(prescription.schedule?.times) 
            ? prescription.schedule.times.filter(time => 
                time && typeof time === 'string' && time.includes(':')
              )
            : [],
          with_food: Boolean(prescription.schedule?.with_food),
          special_instructions: prescription.schedule?.special_instructions?.trim() || '',
        }
      }));
  };

  // Parse medication management content into structured data
  const parseMedicationManagementContent = (content) => {
    if (!content || typeof content !== 'string') {
      return [];
    }

    // Split by periods and clean up
    const medications = content
      .split('.')
      .map(item => item.trim())
      .filter(item => item.length > 0 && item.includes(':'));

    return medications.map((medication, index) => {
      // Split by colon to separate name from details
      const colonIndex = medication.indexOf(':');
      if (colonIndex === -1) return null;

      const name = medication.substring(0, colonIndex).trim();
      const details = medication.substring(colonIndex + 1).trim();

      // Extract dosage (first part usually contains dosage info)
      const dosageMatch = details.match(/(\d+mg?\s*(?:twice|once|daily|three times|bid|tid|qd|qid)?(?:\s*daily)?)/i);
      const dosage = dosageMatch ? dosageMatch[1] : '';

      // Extract frequency
      let frequency = '';
      if (details.includes('twice daily')) frequency = 'Twice daily';
      else if (details.includes('three times daily')) frequency = 'Three times daily';
      else if (details.includes('daily')) frequency = 'Once daily';
      else if (details.includes('bid')) frequency = 'Twice daily';
      else if (details.includes('tid')) frequency = 'Three times daily';
      else if (details.includes('qd') || details.includes('once')) frequency = 'Once daily';

      // Extract timing information
      let timing = '';
      if (details.includes('with food')) timing = 'With food';
      else if (details.includes('with meals')) timing = 'With meals';
      else if (details.includes('before meals')) timing = 'Before meals';
      else if (details.includes('same time')) timing = 'Same time daily';

      // Extract duration
      const durationMatch = details.match(/for\s+(\d+\s*(?:days?|weeks?|months?))/i);
      const duration = durationMatch ? durationMatch[1] : 'Ongoing';

      // Extract special instructions
      let specialInstructions = details;
      // Remove already extracted parts
      if (dosage) specialInstructions = specialInstructions.replace(dosage, '');
      if (timing) specialInstructions = specialInstructions.replace(/with food|with meals|before meals|same time/gi, '');
      specialInstructions = specialInstructions
        .replace(/for\s+\d+\s*(?:days?|weeks?|months?)/gi, '')
        .replace(/^\s*,\s*/, '')
        .trim();

      return {
        id: index + 1,
        name: name,
        dosage: dosage,
        frequency: frequency,
        timing: timing,
        duration: duration,
        instructions: specialInstructions,
        originalText: medication
      };
    }).filter(med => med !== null);
  };

  // Parse lifestyle recommendations content into structured data
  const parseLifestyleRecommendationsContent = (content) => {
    if (!content || typeof content !== 'string') {
      return [];
    }

    // Split by commas and clean up each recommendation
    const recommendations = content
      .split(',')
      .map(item => item.trim())
      .filter(item => item.length > 0);

    return recommendations.map((recommendation, index) => {
      // Categorize recommendations based on keywords
      let category = 'General';
      let icon = '📝';
      let priority = 'medium';

      if (/diet|food|nutrition|sodium|carbohydrate|potassium|sugar|meal/i.test(recommendation)) {
        category = 'Diet & Nutrition';
        icon = '🥗';
        priority = 'high';
      } else if (/fluid|water|drink/i.test(recommendation)) {
        category = 'Fluid Management';
        icon = '💧';
        priority = 'high';
      } else if (/exercise|physical|activity|walk/i.test(recommendation)) {
        category = 'Physical Activity';
        icon = '🏃‍♂️';
        priority = 'medium';
      } else if (/weight|monitor|check|measure/i.test(recommendation)) {
        category = 'Monitoring';
        icon = '📊';
        priority = 'high';
      } else if (/stress|sleep|rest|relax/i.test(recommendation)) {
        category = 'Wellness';
        icon = '😌';
        priority = 'medium';
      } else if (/smoke|alcohol|tobacco/i.test(recommendation)) {
        category = 'Lifestyle Changes';
        icon = '🚭';
        priority = 'high';
      }

      return {
        id: index + 1,
        text: recommendation,
        category: category,
        icon: icon,
        priority: priority,
        originalText: recommendation
      };
    });
  };

  if (!carePlan || !carePlan.care_plan) {
    return (
      <Alert severity="info">
        No care plan data available
      </Alert>
    );
  }

  // Debug the data when component renders
  React.useEffect(() => {
    debugCarePlanData();
  }, [carePlan]);

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

  const parseMedicationFromContent = (content) => {
    // Extract medication information from the care plan content
    // This is a helper function to parse the AI-generated text into structured data
    const medications = [];
    
    // Look for common medication patterns in the content
    const lines = content.split('\n').filter(line => line.trim());
    
    lines.forEach(line => {
      // Try to extract medication name, dosage, frequency, and instructions
      const medicationMatch = line.match(/^-?\s*([A-Za-z\s]+?)[\s:]+([\d\.]+\s*mg|[\d\.]+\s*units?|[\d]+-[\d]+\s*puffs?)[\s,]*(.*?)$/i);
      
      if (medicationMatch) {
        const [, name, dosage, rest] = medicationMatch;
        
        // Try to extract frequency and instructions
        const frequencyMatch = rest.match(/(once|twice|three times|four times|daily|bid|tid|qid|as needed|prn)/i);
        const timingMatch = rest.match(/(\d{1,2}:\d{2})/g);
        const foodMatch = rest.match(/(with food|after meals|before meals|on empty stomach)/i);
        
        medications.push({
          name: name.trim(),
          dosage: dosage.trim(),
          frequency: frequencyMatch ? frequencyMatch[0] : 'As prescribed',
          times: timingMatch || [],
          withFood: foodMatch ? foodMatch[0] : 'No specific requirement',
          instructions: rest.replace(/(once|twice|three times|four times|daily|bid|tid|qid|as needed|prn).*?/i, '').trim() || 'Follow prescription'
        });
      }
    });
    
    return medications;
  };

  const renderMedicationManagement = (section, title, icon) => {
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
                {/* Parse and display medication management content as table */}
                {(() => {
                  const parsedMedications = parseMedicationManagementContent(item.content);
                  
                  if (parsedMedications.length === 0) {
                    return (
                      <Typography variant="body1" sx={{ lineHeight: 1.6, mb: 2 }}>
                        {item.content}
                      </Typography>
                    );
                  }

                  return (
                    <Box>
                      {/* Parsed Medication Table */}
                      <Box sx={{ mb: 3 }}>
                        <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', mb: 2, color: 'secondary.main' }}>
                          <ScheduleIcon sx={{ mr: 1 }} />
                          Medication Schedule
                        </Typography>
                        
                        <TableContainer component={Paper} sx={{ border: '1px solid', borderColor: 'divider' }}>
                          <Table size="small">
                            <TableHead>
                              <TableRow sx={{ bgcolor: 'primary.light' }}>
                                <TableCell sx={{ fontWeight: 'bold', color: 'primary.contrastText' }}>Medication</TableCell>
                                <TableCell sx={{ fontWeight: 'bold', color: 'primary.contrastText' }}>Dosage</TableCell>
                                <TableCell sx={{ fontWeight: 'bold', color: 'primary.contrastText' }}>Frequency</TableCell>
                                <TableCell sx={{ fontWeight: 'bold', color: 'primary.contrastText' }}>Timing</TableCell>
                                <TableCell sx={{ fontWeight: 'bold', color: 'primary.contrastText' }}>Duration</TableCell>
                                <TableCell sx={{ fontWeight: 'bold', color: 'primary.contrastText' }}>Instructions</TableCell>
                              </TableRow>
                            </TableHead>
                            <TableBody>
                              {parsedMedications.map((medication, medIndex) => (
                                <TableRow key={medIndex} hover sx={{ '&:nth-of-type(odd)': { bgcolor: 'action.hover' } }}>
                                  <TableCell sx={{ fontWeight: 'medium' }}>
                                    {medication.name}
                                  </TableCell>
                                  <TableCell>
                                    {medication.dosage}
                                  </TableCell>
                                  <TableCell>
                                    {medication.frequency}
                                  </TableCell>
                                  <TableCell>
                                    {medication.timing}
                                  </TableCell>
                                  <TableCell>
                                    {medication.duration}
                                  </TableCell>
                                  <TableCell sx={{ maxWidth: '200px' }}>
                                    <Typography variant="body2" sx={{ fontSize: '0.875rem' }}>
                                      {medication.instructions}
                                    </Typography>
                                  </TableCell>
                                </TableRow>
                              ))}
                            </TableBody>
                          </Table>
                        </TableContainer>
                      </Box>

                      {/* Original content for reference */}
                      <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                        <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 'medium' }}>
                          Original Content:
                        </Typography>
                        <Typography variant="body2" sx={{ mt: 1, fontStyle: 'italic' }}>
                          {item.content}
                        </Typography>
                      </Box>
                    </Box>
                  );
                })()}
                
                {/* Keep the original medication table from form data if needed */}
                <Box sx={{ mt: 3 }}>
                  <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', mb: 2, color: 'secondary.main' }}>
                    <ScheduleIcon sx={{ mr: 1 }} />
                    Form-Based Medication Schedule
                  </Typography>
                  
                  {carePlan.medical_data && carePlan.medical_data.prescriptions && carePlan.medical_data.prescriptions.length > 0 ? (
                    (() => {
                      const cleanedPrescriptions = cleanMedicationData(carePlan.medical_data.prescriptions);
                      
                      if (cleanedPrescriptions.length === 0) {
                        return (
                          <Paper sx={{ p: 3, textAlign: 'center', bgcolor: 'warning.light' }}>
                            <PharmacyIcon sx={{ fontSize: 48, color: 'warning.dark', mb: 2 }} />
                            <Typography variant="h6" color="warning.dark" gutterBottom>
                              No valid medication data found
                            </Typography>
                            <Typography variant="body2" color="warning.dark">
                              The prescription data appears to contain invalid entries. Please check the medication form.
                            </Typography>
                          </Paper>
                        );
                      }

                      return (
                        <TableContainer component={Paper} sx={{ mt: 2, border: '1px solid', borderColor: 'divider' }}>
                          <Table size="small">
                            <TableHead>
                              <TableRow sx={{ bgcolor: 'primary.light' }}>
                                <TableCell sx={{ fontWeight: 'bold', color: 'primary.contrastText' }}>Medication</TableCell>
                                <TableCell sx={{ fontWeight: 'bold', color: 'primary.contrastText' }}>Dosage</TableCell>
                                <TableCell sx={{ fontWeight: 'bold', color: 'primary.contrastText' }}>Frequency</TableCell>
                                <TableCell sx={{ fontWeight: 'bold', color: 'primary.contrastText' }}>Schedule Times</TableCell>
                                <TableCell sx={{ fontWeight: 'bold', color: 'primary.contrastText' }}>With Food</TableCell>
                                <TableCell sx={{ fontWeight: 'bold', color: 'primary.contrastText' }}>Duration</TableCell>
                                <TableCell sx={{ fontWeight: 'bold', color: 'primary.contrastText' }}>Instructions</TableCell>
                              </TableRow>
                            </TableHead>
                            <TableBody>
                              {cleanedPrescriptions.map((prescription, medIndex) => (
                                <TableRow key={medIndex} hover sx={{ '&:nth-of-type(odd)': { bgcolor: 'action.hover' } }}>
                                  <TableCell>
                                    <Typography variant="body2" sx={{ fontWeight: 'medium', color: 'primary.main' }}>
                                      {prescription.medication_name}
                                    </Typography>
                                  </TableCell>
                                  <TableCell>
                                    <Typography variant="body2">
                                      {prescription.dosage || '-'}
                                    </Typography>
                                  </TableCell>
                                  <TableCell>
                                    <Chip 
                                      label={prescription.schedule?.frequency || 'As prescribed'} 
                                      size="small"
                                      color="primary"
                                      variant="outlined"
                                    />
                                  </TableCell>
                                  <TableCell>
                                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                                      {prescription.schedule?.times?.length > 0 ? (
                                        prescription.schedule.times.map((time, timeIndex) => (
                                          <Chip 
                                            key={timeIndex}
                                            label={time}
                                            size="small"
                                            color="secondary"
                                            variant="outlined"
                                          />
                                        ))
                                      ) : (
                                        <Typography variant="body2" color="textSecondary">-</Typography>
                                      )}
                                    </Box>
                                  </TableCell>
                                  <TableCell>
                                    <Chip 
                                      label={prescription.schedule?.with_food ? 'With Food' : 'Any Time'}
                                      size="small"
                                      color={prescription.schedule?.with_food ? 'success' : 'default'}
                                      variant="outlined"
                                    />
                                  </TableCell>
                                  <TableCell>
                                    <Typography variant="body2">
                                      {prescription.duration || '-'}
                                    </Typography>
                                  </TableCell>
                                  <TableCell>
                                    <Typography variant="body2" sx={{ maxWidth: 200 }}>
                                      {prescription.schedule?.special_instructions || 
                                       prescription.instructions || '-'}
                                    </Typography>
                                  </TableCell>
                                </TableRow>
                              ))}
                            </TableBody>
                          </Table>
                        </TableContainer>
                      );
                    })()
                  ) : (
                    <Paper sx={{ p: 3, textAlign: 'center', bgcolor: 'grey.50' }}>
                      <PharmacyIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
                      <Typography variant="h6" color="textSecondary" gutterBottom>
                        No medication schedule data available
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        Medication details from the original prescription form are not available
                      </Typography>
                    </Paper>
                  )}
                  
                  <Alert severity="info" sx={{ mt: 2 }}>
                    <Typography variant="body2">
                      <strong>📋 Medication Schedule Guide:</strong>
                      <br />• Follow the prescribed times consistently for optimal effectiveness
                      <br />• Set reminders or alarms for each medication time
                      <br />• Take note of food requirements to avoid interactions
                      <br />• Contact healthcare provider if you miss multiple doses
                    </Typography>
                  </Alert>
                </Box>
                
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

  const renderLifestyleRecommendations = (section, title, icon) => {
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
                {/* Parse and display lifestyle recommendations as categorized boxes */}
                {(() => {
                  const parsedRecommendations = parseLifestyleRecommendationsContent(item.content);
                  
                  if (parsedRecommendations.length === 0) {
                    return (
                      <Typography variant="body1" sx={{ lineHeight: 1.6, mb: 2 }}>
                        {item.content}
                      </Typography>
                    );
                  }

                  // Group recommendations by category
                  const groupedRecommendations = parsedRecommendations.reduce((groups, rec) => {
                    const category = rec.category;
                    if (!groups[category]) {
                      groups[category] = [];
                    }
                    groups[category].push(rec);
                    return groups;
                  }, {});

                  return (
                    <Box>
                      {/* Categorized Lifestyle Recommendations */}
                      <Box sx={{ mb: 3 }}>
                        <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', mb: 2, color: 'secondary.main' }}>
                          <FitnessIcon sx={{ mr: 1 }} />
                          Lifestyle Recommendations
                        </Typography>
                        
                        <Grid container spacing={2}>
                          {Object.entries(groupedRecommendations).map(([category, recommendations]) => (
                            <Grid item xs={12} md={6} key={category}>
                              <Paper 
                                elevation={1} 
                                sx={{ 
                                  p: 2, 
                                  borderLeft: 4, 
                                  borderLeftColor: recommendations[0].priority === 'high' ? 'error.main' : 
                                                   recommendations[0].priority === 'medium' ? 'warning.main' : 'success.main',
                                  height: '100%',
                                  bgcolor: recommendations[0].priority === 'high' ? 'error.light' : 
                                           recommendations[0].priority === 'medium' ? 'warning.light' : 'success.light',
                                  bgcolor: 'background.paper'
                                }}
                              >
                                <Typography 
                                  variant="subtitle1" 
                                  sx={{ 
                                    fontWeight: 'bold', 
                                    mb: 1.5,
                                    display: 'flex',
                                    alignItems: 'center',
                                    color: recommendations[0].priority === 'high' ? 'error.dark' : 
                                           recommendations[0].priority === 'medium' ? 'warning.dark' : 'success.dark'
                                  }}
                                >
                                  <span style={{ marginRight: '8px', fontSize: '1.2em' }}>
                                    {recommendations[0].icon}
                                  </span>
                                  {category}
                                  <Chip
                                    label={recommendations[0].priority}
                                    size="small"
                                    color={
                                      recommendations[0].priority === 'high' ? 'error' :
                                      recommendations[0].priority === 'medium' ? 'warning' : 'success'
                                    }
                                    sx={{ ml: 'auto' }}
                                  />
                                </Typography>
                                
                                {recommendations.map((rec, recIndex) => (
                                  <Box key={recIndex} sx={{ mb: 1.5 }}>
                                    <Typography variant="body2" sx={{ 
                                      display: 'flex', 
                                      alignItems: 'flex-start',
                                      lineHeight: 1.4
                                    }}>
                                      <Box component="span" sx={{ 
                                        minWidth: '8px', 
                                        height: '8px', 
                                        borderRadius: '50%', 
                                        bgcolor: 'primary.main',
                                        display: 'inline-block',
                                        mt: 0.75,
                                        mr: 1,
                                        flexShrink: 0
                                      }} />
                                      {rec.text}
                                    </Typography>
                                  </Box>
                                ))}
                              </Paper>
                            </Grid>
                          ))}
                        </Grid>
                      </Box>

                      {/* Original content for reference */}
                      <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                        <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 'medium' }}>
                          Original Content:
                        </Typography>
                        <Typography variant="body2" sx={{ mt: 1, fontStyle: 'italic' }}>
                          {item.content}
                        </Typography>
                      </Box>
                    </Box>
                  );
                })()}
              </AccordionDetails>
            </Accordion>
          ))}
        </CardContent>
      </Card>
    );
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
          {renderMedicationManagement(
            care_plan.medication_management,
            'Medication Management',
            <PharmacyIcon color="secondary" />
          )}
        </Grid>
        
        <Grid item xs={12}>
          {renderLifestyleRecommendations(
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