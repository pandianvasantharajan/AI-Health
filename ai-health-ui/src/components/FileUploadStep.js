import React, { useState, useCallback } from 'react';
import {
  Box,
  Typography,
  Button,
  Paper,
  Alert,
  LinearProgress,
  Chip,
  Grid,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemIcon,
  ListItemText
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  InsertDriveFile as FileIcon,
  Description as PrescriptionIcon,
  Assignment as ReportIcon,
  LocalHospital as MedicalIcon,
  CheckCircle as CheckIcon
} from '@mui/icons-material';

const FileUploadStep = ({ onFileUploaded, uploadedFile }) => {
  const [file, setFile] = useState(uploadedFile);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const [dragOver, setDragOver] = useState(false);

  const acceptedFileTypes = [
    'application/pdf',
    'image/jpeg',
    'image/png',
    'image/jpg',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
  ];

  const maxFileSize = 10 * 1024 * 1024; // 10MB

  const handleFileSelect = (selectedFile) => {
    setError('');
    
    if (!selectedFile) return;

    // Validate file type
    if (!acceptedFileTypes.includes(selectedFile.type)) {
      setError('Please upload a valid file type (PDF, JPG, PNG, DOC, DOCX)');
      return;
    }

    // Validate file size
    if (selectedFile.size > maxFileSize) {
      setError('File size must be less than 10MB');
      return;
    }

    setFile(selectedFile);
  };

  const handleFileUpload = async () => {
    if (!file) return;

    setUploading(true);
    setError('');

    try {
      const formData = new FormData();
      formData.append('file', file);

      // Use different API base URL for development vs production
      const apiBaseUrl = process.env.NODE_ENV === 'development' ? 'http://localhost:8000' : '';
      const response = await fetch(`${apiBaseUrl}/upload/file`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.status}`);
      }

      const data = await response.json();
      
      // Call parent component with file and S3 URL
      onFileUploaded(file, data.file_url || data.s3_url);
      
    } catch (error) {
      console.error('Upload error:', error);
      setError(`Upload failed: ${error.message}`);
    } finally {
      setUploading(false);
    }
  };

  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    setDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e) => {
    e.preventDefault();
    setDragOver(false);
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setDragOver(false);
    const droppedFile = e.dataTransfer.files[0];
    handleFileSelect(droppedFile);
  }, []);

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const supportedDocuments = [
    { icon: <PrescriptionIcon color="primary" />, text: 'Prescription Documents' },
    { icon: <ReportIcon color="secondary" />, text: 'Medical Reports' },
    { icon: <MedicalIcon color="success" />, text: 'Lab Results' },
    { icon: <FileIcon color="info" />, text: 'Clinical Notes' }
  ];

  return (
    <Box>
      <Typography variant="h5" gutterBottom sx={{ mb: 3 }}>
        Upload Medical Documents
      </Typography>

      <Grid container spacing={3}>
        {/* Upload Area */}
        <Grid item xs={12} md={8}>
          <Paper
            elevation={dragOver ? 8 : 2}
            sx={{
              p: 4,
              textAlign: 'center',
              border: dragOver ? '2px dashed primary.main' : '2px dashed grey.300',
              bgcolor: dragOver ? 'primary.light' : 'grey.50',
              cursor: 'pointer',
              transition: 'all 0.3s ease',
              '&:hover': {
                bgcolor: 'grey.100',
                borderColor: 'primary.main'
              }
            }}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => document.getElementById('file-input').click()}
          >
            <input
              id="file-input"
              type="file"
              accept=".pdf,.jpg,.jpeg,.png,.doc,.docx"
              style={{ display: 'none' }}
              onChange={(e) => handleFileSelect(e.target.files[0])}
            />

            <UploadIcon sx={{ fontSize: 64, color: 'primary.main', mb: 2 }} />
            
            <Typography variant="h6" gutterBottom>
              {dragOver ? 'Drop your file here' : 'Drag & drop your medical file here'}
            </Typography>
            
            <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
              or click to browse files
            </Typography>

            <Box sx={{ display: 'flex', justifyContent: 'center', gap: 1, flexWrap: 'wrap' }}>
              {['PDF', 'JPG', 'PNG', 'DOC', 'DOCX'].map((type) => (
                <Chip key={type} label={type} size="small" variant="outlined" />
              ))}
            </Box>

            <Typography variant="caption" display="block" sx={{ mt: 1, color: 'textSecondary' }}>
              Maximum file size: 10MB
            </Typography>
          </Paper>

          {/* File Preview */}
          {file && (
            <Paper sx={{ p: 3, mt: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <FileIcon sx={{ mr: 2, color: 'primary.main' }} />
                <Box sx={{ flexGrow: 1 }}>
                  <Typography variant="body1" fontWeight="bold">
                    {file.name}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    {formatFileSize(file.size)} • {file.type}
                  </Typography>
                </Box>
                <CheckIcon sx={{ color: 'success.main' }} />
              </Box>

              {uploading && (
                <Box sx={{ mb: 2 }}>
                  <LinearProgress />
                  <Typography variant="body2" sx={{ mt: 1 }} align="center">
                    Uploading to secure cloud storage...
                  </Typography>
                </Box>
              )}

              <Button
                variant="contained"
                fullWidth
                onClick={handleFileUpload}
                disabled={uploading}
                startIcon={<UploadIcon />}
                size="large"
              >
                {uploading ? 'Uploading...' : 'Upload & Continue'}
              </Button>
            </Paper>
          )}

          {/* Error Display */}
          {error && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {error}
            </Alert>
          )}
        </Grid>

        {/* Supported Documents Info */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Supported Documents
              </Typography>
              <List dense>
                {supportedDocuments.map((doc, index) => (
                  <ListItem key={index}>
                    <ListItemIcon>
                      {doc.icon}
                    </ListItemIcon>
                    <ListItemText primary={doc.text} />
                  </ListItem>
                ))}
              </List>
              
              <Typography variant="body2" color="textSecondary" sx={{ mt: 2 }}>
                💡 <strong>Tip:</strong> For best results, ensure documents are clear and readable. The system will automatically extract medical information using AI.
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default FileUploadStep;