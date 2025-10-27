# AI Health UI

# AI Health Care Plan Generator - React UI

A modern React application with Material UI components for generating AI-powered care plans using medical factor analysis.

## 🚀 Features

- **Medical Factor Input**: Comprehensive form for patient information
- **Material UI Design**: Modern, responsive interface
- **Nova Micro Integration**: Direct integration with Amazon Nova Micro API
- **Care Plan Display**: Beautiful, organized care plan results
- **Real-time Feedback**: Loading states and error handling
- **Print Support**: Print-friendly care plan format

## 📋 Medical Factors Supported

The application collects and processes:

### Patient Information
- Age, Gender, Weight
- Medical Conditions (multiple)
- Allergies (multiple)
- Prescription Date

### Medical Details
- Primary Diagnosis
- Multiple Prescriptions:
  - Medication Name
  - Dosage
  - Duration
  - Instructions
- Doctor Notes

## 🛠️ Technology Stack

- **React 18** - Modern React with hooks
- **Material UI v5** - Google Material Design components
- **Date-fns** - Date manipulation library
- **Axios** - HTTP client for API calls
- **React Scripts** - Development and build tools

## 🏃‍♂️ Quick Start

### Prerequisites

- Node.js 16+ and npm
- AI Health Service running on `http://localhost:8000`

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm start

# Build for production
npm run build
```

### Environment Setup

The application expects the AI Health Service to be running on `http://localhost:8000`. 
The proxy configuration in `package.json` handles API routing.

## 🎯 Usage

1. **Fill Patient Information**
   - Enter basic patient details
   - Add medical conditions by typing and clicking "+"
   - Add allergies with the same method

2. **Enter Diagnosis**
   - Provide the primary diagnosis

3. **Add Prescriptions**
   - Fill in medication details
   - Add multiple prescriptions as needed
   - Remove prescriptions with the delete button

4. **Add Doctor Notes**
   - Optional additional information

5. **Generate Care Plan**
   - Click "Generate Care Plan with Nova Micro"
   - View results in organized sections below

## 📊 API Integration

### Endpoint Used
```
POST /care-plan/nova-micro
```

### Request Format
```json
{
  "patient_info": {
    "age": 65,
    "gender": "Female",
    "weight": 68.0,
    "medical_conditions": ["Hypertension", "Diabetes"],
    "allergies": ["Penicillin"]
  },
  "diagnosis": "Acute heart failure exacerbation",
  "prescriptions": [
    {
      "medication_name": "Furosemide",
      "dosage": "40mg twice daily",
      "duration": "14 days",
      "instructions": "Take with food"
    }
  ],
  "doctor_notes": "Monitor closely",
  "prescription_date": "2025-10-27"
}
```

### Response Format
```json
{
  "success": true,
  "message": "Care plan generated successfully",
  "care_plan": {
    "summary": "Comprehensive care plan...",
    "treatment_plan": [...],
    "medication_management": [...],
    "lifestyle_recommendations": [...],
    "follow_up_recommendations": [...]
  },
  "model_used": "amazon.nova-micro-v1:0",
  "model_type": "Amazon Nova Micro"
}
```

## 🎨 Component Structure

```
src/
├── App.js                    # Main application component
├── App.css                   # Application styles
├── index.js                  # React entry point
└── components/
    ├── MedicalFactorForm.js  # Medical information form
    └── CarePlanResult.js     # Care plan display component
```

### Key Components

**MedicalFactorForm**
- Comprehensive form with validation
- Dynamic prescription management
- Medical conditions and allergies chips
- Date picker for prescription date
- Real-time form validation

**CarePlanResult**
- Expandable care plan sections
- Print functionality
- Model information display
- Detailed view dialogs
- Progress indicators

## 🔧 Configuration

### Development Server
- Port: 3000 (default)
- Proxy: API calls to `http://localhost:8000`
- Hot reloading enabled

### Build Configuration
- Optimized production builds
- Code splitting
- PWA support (via manifest.json)

## 🎯 Medical Factor Analysis

This UI is specifically designed for Amazon Nova Micro's medical factor analysis capabilities:

- **Complex Comorbidities**: Handle multiple medical conditions
- **Drug Interactions**: Support for comprehensive medication analysis
- **Patient-Specific Factors**: Age, weight, and allergy considerations
- **Care Coordination**: Multi-faceted treatment planning

## 📱 Responsive Design

- **Mobile-First**: Optimized for mobile devices
- **Tablet Support**: Adapted layouts for tablets
- **Desktop**: Full-featured desktop experience
- **Print-Friendly**: Optimized print styles for care plans

## 🔒 Error Handling

- **Network Errors**: Clear error messages for connection issues
- **API Errors**: Detailed error feedback from the backend
- **Form Validation**: Real-time validation with helpful hints
- **Loading States**: Visual feedback during API calls

## 🎨 UI/UX Features

- **Material Design**: Consistent Google Material Design
- **Accessibility**: ARIA labels and keyboard navigation
- **Dark Mode Ready**: Theme system prepared for dark mode
- **Animations**: Smooth transitions and feedback
- **Icons**: Comprehensive icon set for medical contexts

## 🚀 Deployment

### Production Build
```bash
npm run build
```

### Deployment Options
- **Static Hosting**: Serve the `build` folder
- **Docker**: Create containerized deployment
- **CDN**: Deploy to CDN for global distribution

## 🔧 Customization

### Themes
Modify `src/index.js` to customize Material UI theme:
```javascript
const theme = createTheme({
  palette: {
    primary: { main: '#1976d2' },
    secondary: { main: '#dc004e' }
  }
});
```

### API Endpoint
Update proxy in `package.json` for different backend URLs:
```json
{
  "proxy": "http://your-api-server:8000"
}
```

## 📄 License

This project is part of the AI Health Service ecosystem.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For support with the React UI:
- Check browser console for errors
- Ensure AI Health Service is running
- Verify network connectivity
- Review component props and state

---

**AI Health Care Plan Generator** - Modern React interface for AI-powered medical care plan generation with Amazon Nova Micro integration.