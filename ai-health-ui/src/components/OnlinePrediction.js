import React, { useState } from 'react';
import {
  Box,
  Stepper,
  Step,
  StepLabel,
  Button,
  Typography,
  Paper,
  Container
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  Visibility as PreviewIcon,
  LocalHospital as CarePlanIcon
} from '@mui/icons-material';
import FileUploadStep from './FileUploadStep';
import PreviewStep from './PreviewStep';
import NewCarePlanStep from './NewCarePlanStep';

const steps = [
  {
    label: 'Upload Medical File',
    icon: <UploadIcon />,
    description: 'Upload prescription or medical documents'
  },
  {
    label: 'Preview & Extract',
    icon: <PreviewIcon />,
    description: 'Review and extract medical data'
  },
  {
    label: 'Generate Care Plan',
    icon: <CarePlanIcon />,
    description: 'Create personalized care plan'
  }
];

const OnlinePrediction = () => {
  const [activeStep, setActiveStep] = useState(0);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [s3FileUrl, setS3FileUrl] = useState('');
  const [extractedData, setExtractedData] = useState(null);
  const [carePlan, setCarePlan] = useState(null);

  const handleNext = () => {
    setActiveStep((prevActiveStep) => prevActiveStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };

  const handleReset = () => {
    setActiveStep(0);
    setUploadedFile(null);
    setS3FileUrl('');
    setExtractedData(null);
    setCarePlan(null);
  };

  const handleFileUpload = (file, fileUrl) => {
    setUploadedFile(file);
    setS3FileUrl(fileUrl);
    handleNext();
  };

  const handleDataExtracted = (data) => {
    setExtractedData(data);
    // Don't automatically advance step - let user decide when to continue
  };

  const handleProceedToCarePlan = () => {
    if (extractedData) {
      handleNext();
    }
  };

  const handleCarePlanGenerated = (plan) => {
    setCarePlan(plan);
  };

  const getStepContent = (step) => {
    switch (step) {
      case 0:
        return (
          <FileUploadStep
            onFileUploaded={handleFileUpload}
            uploadedFile={uploadedFile}
          />
        );
      case 1:
        return (
          <PreviewStep
            s3FileUrl={s3FileUrl}
            uploadedFile={uploadedFile}
            onDataExtracted={handleDataExtracted}
            onProceedToCarePlan={handleProceedToCarePlan}
            extractedData={extractedData}
            onBack={handleBack}
          />
        );
      case 2:
        return (
          <NewCarePlanStep
            extractedData={extractedData}
            onCarePlanGenerated={handleCarePlanGenerated}
            carePlan={carePlan}
            onBack={handleBack}
          />
        );
      default:
        return 'Unknown step';
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom color="primary" sx={{ mb: 4 }}>
        Online Medical Prediction
      </Typography>

      <Paper elevation={3} sx={{ p: 3 }}>
        {/* Stepper */}
        <Stepper activeStep={activeStep} alternativeLabel sx={{ mb: 4 }}>
          {steps.map((step, index) => {
            const canNavigate = () => {
              if (index === 0) return true; // Always can go to upload
              if (index === 1) return uploadedFile && s3FileUrl; // Can go to preview if file uploaded
              if (index === 2) return extractedData; // Can go to care plan if data extracted
              return false;
            };

            return (
              <Step key={step.label}>
                <StepLabel
                  icon={step.icon}
                  sx={{
                    '& .MuiStepIcon-root': {
                      fontSize: '1.5rem',
                      cursor: canNavigate() ? 'pointer' : 'default',
                    },
                    cursor: canNavigate() ? 'pointer' : 'default',
                  }}
                  onClick={() => canNavigate() && setActiveStep(index)}
                >
                  <Typography 
                    variant="body1" 
                    fontWeight="bold"
                    sx={{ cursor: canNavigate() ? 'pointer' : 'default' }}
                  >
                    {step.label}
                  </Typography>
                  <Typography 
                    variant="caption" 
                    color="textSecondary"
                    sx={{ cursor: canNavigate() ? 'pointer' : 'default' }}
                  >
                    {step.description}
                  </Typography>
                </StepLabel>
              </Step>
            );
          })}
        </Stepper>

        {/* Step Content */}
        <Box sx={{ minHeight: '400px' }}>
          {activeStep === steps.length ? (
            // Completion Screen
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <Typography variant="h5" gutterBottom color="success.main">
                🎉 Care Plan Generated Successfully!
              </Typography>
              <Typography variant="body1" sx={{ mb: 3 }}>
                Your personalized care plan has been created based on the uploaded medical documents.
              </Typography>
              <Button
                variant="contained"
                onClick={handleReset}
                size="large"
                startIcon={<UploadIcon />}
              >
                Start New Prediction
              </Button>
            </Box>
          ) : (
            getStepContent(activeStep)
          )}
        </Box>
      </Paper>
    </Box>
  );
};

export default OnlinePrediction;