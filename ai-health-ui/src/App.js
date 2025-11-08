import React, { useState } from 'react';
import { 
  Box, 
  CssBaseline, 
  createTheme, 
  ThemeProvider,
  Drawer,
  AppBar,
  Toolbar,
  Typography,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Container,
  IconButton,
  Tooltip
} from '@mui/material';
import { 
  LocalHospital as CarePlanIcon,
  Settings as SettingsIcon,
  Menu as MenuIcon,
  ChevronLeft as ChevronLeftIcon,
  ChevronRight as ChevronRightIcon,
  OnlinePrediction as OnlinePredictionIcon
} from '@mui/icons-material';
import { BrowserRouter as Router, Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import CarePlan from './components/CarePlan';
import OnlinePrediction from './components/OnlinePrediction';
import Settings from './components/Settings';
import './App.css';

// Create a custom theme
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

const drawerWidth = 240;
const miniDrawerWidth = 64;

const NavigationDrawer = ({ open, handleDrawerToggle }) => {
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    {
      text: 'Care Plan',
      icon: <CarePlanIcon />,
      path: '/'
    },
    {
      text: 'Online Prediction',
      icon: <OnlinePredictionIcon />,
      path: '/online-prediction'
    },
    {
      text: 'Settings',
      icon: <SettingsIcon />,
      path: '/settings'
    }
  ];

  return (
    <Drawer
      variant="permanent"
      open={open}
      sx={{
        width: open ? drawerWidth : miniDrawerWidth,
        flexShrink: 0,
        whiteSpace: 'nowrap',
        boxSizing: 'border-box',
        transition: 'width 0.3s',
        '& .MuiDrawer-paper': {
          width: open ? drawerWidth : miniDrawerWidth,
          boxSizing: 'border-box',
          top: 64, // Height of AppBar
          height: 'calc(100vh - 64px)',
          transition: 'width 0.3s',
          overflowX: 'hidden',
        },
      }}
    >
      {/* Toggle Button */}
      <Box sx={{ display: 'flex', justifyContent: 'flex-end', p: 1 }}>
        <IconButton onClick={handleDrawerToggle} size="small">
          {open ? <ChevronLeftIcon /> : <ChevronRightIcon />}
        </IconButton>
      </Box>

      <List>
        {menuItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            <Tooltip title={!open ? item.text : ''} placement="right">
              <ListItemButton 
                selected={location.pathname === item.path}
                onClick={() => navigate(item.path)}
                sx={{
                  minHeight: 48,
                  justifyContent: open ? 'initial' : 'center',
                  px: 2.5,
                  '&.Mui-selected': {
                    backgroundColor: 'primary.light',
                    '&:hover': {
                      backgroundColor: 'primary.light',
                    },
                  },
                }}
              >
                <ListItemIcon 
                  sx={{ 
                    minWidth: 0,
                    mr: open ? 3 : 'auto',
                    justifyContent: 'center',
                    color: location.pathname === item.path ? 'primary.main' : 'inherit' 
                  }}
                >
                  {item.icon}
                </ListItemIcon>
                <ListItemText 
                  primary={item.text}
                  sx={{ 
                    opacity: open ? 1 : 0,
                    '& .MuiListItemText-primary': {
                      fontWeight: location.pathname === item.path ? 'bold' : 'normal',
                      color: location.pathname === item.path ? 'primary.main' : 'inherit'
                    }
                  }}
                />
              </ListItemButton>
            </Tooltip>
          </ListItem>
        ))}
      </List>
    </Drawer>
  );
};

const AppContent = () => {
  const [drawerOpen, setDrawerOpen] = useState(false);

  const handleDrawerToggle = () => {
    setDrawerOpen(!drawerOpen);
  };

  return (
    <Box sx={{ display: 'flex' }}>
      <CssBaseline />
      
      {/* Header */}
      <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="toggle drawer"
            onClick={handleDrawerToggle}
            edge="start"
            sx={{ mr: 2 }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap component="div">
            🏥 AI-Health-AI
          </Typography>
        </Toolbar>
      </AppBar>

      {/* Navigation Drawer */}
      <NavigationDrawer open={drawerOpen} handleDrawerToggle={handleDrawerToggle} />

      {/* Main Content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 0,
          mt: 8, // AppBar height
          ml: drawerOpen ? `${drawerWidth}px` : `${miniDrawerWidth}px`,
          width: drawerOpen ? `calc(100% - ${drawerWidth}px)` : `calc(100% - ${miniDrawerWidth}px)`,
          transition: 'margin 0.3s, width 0.3s',
        }}
      >
        <Routes>
          <Route path="/" element={<CarePlan />} />
          <Route path="/online-prediction" element={<OnlinePrediction />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </Box>
    </Box>
  );
};

function App() {
  return (
    <ThemeProvider theme={theme}>
      <LocalizationProvider dateAdapter={AdapterDateFns}>
        <Router>
          <AppContent />
        </Router>
      </LocalizationProvider>
    </ThemeProvider>
  );
}

export default App;