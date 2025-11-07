import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Chip,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Switch,
  FormControlLabel,
  TextField,
  Button,
  Alert
} from '@mui/material';
import {
  Settings as SettingsIcon,
  Memory as ModelIcon,
  Speed as PerformanceIcon,
  Security as SecurityIcon,
  Save as SaveIcon,
  Psychology as AIIcon
} from '@mui/icons-material';

const Settings = () => {
  const [selectedModel, setSelectedModel] = useState('amazon.nova-micro-v1:0');
  const [temperature, setTemperature] = useState(0.7);
  const [maxTokens, setMaxTokens] = useState(2048);
  const [enableStreaming, setEnableStreaming] = useState(false);
  const [enableDebugMode, setEnableDebugMode] = useState(false);
  const [saved, setSaved] = useState(false);

  const availableModels = [
    {
      id: 'amazon.nova-micro-v1:0',
      name: 'Amazon Nova Micro',
      description: 'Fast, lightweight model for medical factor analysis',
      provider: 'Amazon Bedrock',
      type: 'Medical Specialized',
      maxTokens: 4096,
      cost: 'Low'
    },
    {
      id: 'anthropic.claude-3-sonnet-20240229-v1:0',
      name: 'Claude 3 Sonnet',
      description: 'Balanced performance for comprehensive care plans',
      provider: 'Anthropic',
      type: 'General Purpose',
      maxTokens: 8192,
      cost: 'Medium'
    },
    {
      id: 'anthropic.claude-3-5-sonnet-20241022-v2:0',
      name: 'Claude 3.5 Sonnet',
      description: 'Advanced reasoning for complex medical cases',
      provider: 'Anthropic',
      type: 'Advanced',
      maxTokens: 8192,
      cost: 'High'
    }
  ];

  const handleModelChange = (event) => {
    setSelectedModel(event.target.value);
    setSaved(false);
  };

  const handleSaveSettings = () => {
    // Here you would save to backend or localStorage
    console.log('Saving settings:', {
      selectedModel,
      temperature,
      maxTokens,
      enableStreaming,
      enableDebugMode
    });
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  const selectedModelInfo = availableModels.find(model => model.id === selectedModel);

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', mb: 4 }}>
        <SettingsIcon sx={{ mr: 2 }} />
        Settings
      </Typography>

      {saved && (
        <Alert severity="success" sx={{ mb: 3 }}>
          Settings saved successfully!
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Model Configuration */}
        <Grid item xs={12} md={8}>
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                <ModelIcon sx={{ mr: 1 }} />
                AI Model Configuration
              </Typography>

              <FormControl fullWidth sx={{ mb: 3 }}>
                <InputLabel>Select AI Model</InputLabel>
                <Select
                  value={selectedModel}
                  label="Select AI Model"
                  onChange={handleModelChange}
                >
                  {availableModels.map((model) => (
                    <MenuItem key={model.id} value={model.id}>
                      <Box>
                        <Typography variant="body1">{model.name}</Typography>
                        <Typography variant="caption" color="textSecondary">
                          {model.description}
                        </Typography>
                      </Box>
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              {selectedModelInfo && (
                <Paper sx={{ p: 2, mb: 3, bgcolor: 'grey.50' }}>
                  <Typography variant="h6" gutterBottom>
                    {selectedModelInfo.name}
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={6}>
                      <Typography variant="body2" color="textSecondary">
                        <strong>Provider:</strong> {selectedModelInfo.provider}
                      </Typography>
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <Typography variant="body2" color="textSecondary">
                        <strong>Type:</strong> {selectedModelInfo.type}
                      </Typography>
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <Typography variant="body2" color="textSecondary">
                        <strong>Max Tokens:</strong> {selectedModelInfo.maxTokens}
                      </Typography>
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <Typography variant="body2" color="textSecondary">
                        <strong>Cost:</strong> <Chip label={selectedModelInfo.cost} size="small" />
                      </Typography>
                    </Grid>
                  </Grid>
                  <Typography variant="body2" sx={{ mt: 2 }}>
                    {selectedModelInfo.description}
                  </Typography>
                </Paper>
              )}

              <Grid container spacing={3}>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Temperature"
                    type="number"
                    value={temperature}
                    onChange={(e) => {
                      setTemperature(parseFloat(e.target.value));
                      setSaved(false);
                    }}
                    inputProps={{ min: 0, max: 1, step: 0.1 }}
                    helperText="Controls randomness (0.0 = deterministic, 1.0 = creative)"
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Max Tokens"
                    type="number"
                    value={maxTokens}
                    onChange={(e) => {
                      setMaxTokens(parseInt(e.target.value));
                      setSaved(false);
                    }}
                    inputProps={{ min: 256, max: selectedModelInfo?.maxTokens || 4096 }}
                    helperText="Maximum response length"
                  />
                </Grid>
              </Grid>
            </CardContent>
          </Card>

          {/* Advanced Settings */}
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                <PerformanceIcon sx={{ mr: 1 }} />
                Advanced Settings
              </Typography>

              <List>
                <ListItem>
                  <ListItemIcon>
                    <AIIcon />
                  </ListItemIcon>
                  <ListItemText
                    primary="Enable Streaming"
                    secondary="Stream responses in real-time for faster perceived performance"
                  />
                  <FormControlLabel
                    control={
                      <Switch
                        checked={enableStreaming}
                        onChange={(e) => {
                          setEnableStreaming(e.target.checked);
                          setSaved(false);
                        }}
                      />
                    }
                    label=""
                  />
                </ListItem>
                
                <Divider />
                
                <ListItem>
                  <ListItemIcon>
                    <SecurityIcon />
                  </ListItemIcon>
                  <ListItemText
                    primary="Debug Mode"
                    secondary="Show detailed API responses and error information"
                  />
                  <FormControlLabel
                    control={
                      <Switch
                        checked={enableDebugMode}
                        onChange={(e) => {
                          setEnableDebugMode(e.target.checked);
                          setSaved(false);
                        }}
                      />
                    }
                    label=""
                  />
                </ListItem>
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Model Comparison Sidebar */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Model Comparison
              </Typography>
              <List dense>
                {availableModels.map((model) => (
                  <ListItem 
                    key={model.id}
                    sx={{ 
                      border: model.id === selectedModel ? '2px solid primary.main' : '1px solid grey.300',
                      borderRadius: 1,
                      mb: 1,
                      bgcolor: model.id === selectedModel ? 'primary.light' : 'background.paper'
                    }}
                  >
                    <ListItemText
                      primary={
                        <Typography variant="body2" fontWeight="bold">
                          {model.name}
                        </Typography>
                      }
                      secondary={
                        <Box>
                          <Typography variant="caption" display="block">
                            {model.provider}
                          </Typography>
                          <Chip 
                            label={model.cost} 
                            size="small" 
                            color={model.cost === 'Low' ? 'success' : model.cost === 'Medium' ? 'warning' : 'error'}
                            sx={{ mt: 0.5 }}
                          />
                        </Box>
                      }
                    />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Save Button */}
      <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 3 }}>
        <Button
          variant="contained"
          startIcon={<SaveIcon />}
          onClick={handleSaveSettings}
          size="large"
        >
          Save Settings
        </Button>
      </Box>
    </Box>
  );
};

export default Settings;