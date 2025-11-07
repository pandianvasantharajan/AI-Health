# AI Health Monorepo

A comprehensive healthcare service platform featuring Python-based microservices for file management and AI-powered care plan generation, with a React frontend for user interaction.

## 🏗️ Architecture Overview

```
AI-Health/
├── ai-health-service/     # Python FastAPI backend service
│   ├── app/
│   │   ├── modules/
│   │   │   ├── file_upload.py    # S3 file upload functionality
│   │   │   └── care_plan.py      # AI care plan generation
│   │   ├── main.py               # FastAPI application
│   │   └── config.py             # Configuration management
│   ├── tests/                    # Comprehensive test suite
│   ├── pyproject.toml            # Poetry dependency management
│   └── requirements.txt          # Python dependencies
└── ai-health-ui/          # React frontend
    ├── src/
    │   ├── components/           # React components
    │   │   ├── MedicalFactorForm.js  # Medical form with prefill
    │   │   └── CarePlanResult.js     # Care plan display
    │   ├── App.js               # Main React application
    │   └── index.js             # React entry point
    ├── public/                  # Static assets
    └── package.json             # Node.js dependencies
```

## 🚀 Features

### ✅ Core Services
- **File Upload Service**: Secure S3 integration with PDF validation
- **AI Care Plan Generation**: Amazon Bedrock integration for medical care plans
- **Health Monitoring**: Real-time service health checks and diagnostics
- **API Documentation**: Auto-generated Swagger/OpenAPI documentation
- **React UI**: Modern Material UI interface with medication scheduling

### ✅ Technology Stack
- **Backend**: FastAPI (Python 3.8.1+) with async support
- **Frontend**: React 18 with Material UI v5 components
- **Dependency Management**: Poetry for Python, npm for Node.js
- **Cloud Services**: AWS S3 for storage, Amazon Bedrock for AI/ML
- **Data Validation**: Pydantic for structured data models
- **Testing**: pytest with comprehensive test coverage

### ✅ AI/ML Capabilities
- **Amazon Bedrock Integration**: Multiple foundation models for care plan generation
- **Medical Data Models**: Structured prescription and patient information
- **Care Plan Templates**: Comprehensive healthcare management plans
- **Multiple AI Models**: Support for Claude 4.5, 3.7, 3.5, 3 Sonnet models and Amazon Nova Micro
- **Medical Factors Analysis**: Specialized handling of complex multi-comorbidity cases
- **Medication Scheduling**: Advanced table-based medication management

## 🛠️ Quick Start

### Prerequisites
- Python 3.8.1+ 
- Node.js 16+ and npm
- AWS credentials (for S3 and Bedrock access)

### Backend Setup
```bash
# Clone the repository
git clone <repository-url>
cd AI-Health/ai-health-service

# Install dependencies with Poetry
poetry install

# Set up environment variables
cp .env.example .env
# Edit .env with your AWS credentials

# Run the backend service
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup
```bash
# In a new terminal, navigate to the UI directory
cd AI-Health/ai-health-ui

# Install dependencies
npm install

# Start the React development server
npm start

# UI will be available at http://localhost:3000
```

### Local Development
```bash
cd ai-health-service

# Install dependencies with Poetry
poetry install

# Set up environment variables
cp .env.example .env
# Edit .env with your AWS credentials

# Run the service
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 📚 API Documentation

### Interactive Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

### Available Endpoints

#### Health & Status
- `GET /health` - Service health check
- `GET /` - Welcome message

#### File Upload
- `POST /upload/pdf` - Upload PDF files to S3
- `POST /upload/file` - Upload any file type to S3
- `GET /file/{bucket_name}/{file_key}` - Generate presigned URLs

#### AI Care Plan Generation
- `POST /care-plan/generate` - Generate care plan from prescription
- `POST /care-plan/sample` - Generate sample care plan
- `POST /care-plan/demo` - Demo care plan (no Bedrock required)
- `GET /care-plan/models` - List available AI models

## 🧪 Testing

### Run All Tests
```bash
# Comprehensive test suite
cd ai-health-service
python -m pytest tests/ -v

# Test specific functionality
python tests/test_care_plan.py  # Care plan module tests
python demo_complete.py         # Complete functionality demo
```

### Manual Testing
```bash
# Health check
curl http://localhost:8000/health

# Demo care plan (no AWS required)
curl -X POST http://localhost:8000/care-plan/demo

# Available AI models
curl http://localhost:8000/care-plan/models
```

## ⚙️ Configuration

### Environment Variables
```bash
# AWS Configuration
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1

# S3 Configuration
S3_BUCKET_NAME=your-bucket-name

# Bedrock Configuration
BEDROCK_REGION=us-east-1
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
```

### AWS Setup
1. **S3 Bucket**: Create bucket for file storage
2. **Bedrock Access**: Enable Bedrock in your AWS region
3. **IAM Permissions**: Set up appropriate policies (see CARE_PLAN_GUIDE.md)

## 📋 Care Plan Module

### Features
- **Structured Medical Data**: Pydantic models for prescriptions and patient info
- **AI-Generated Plans**: Amazon Bedrock integration with Claude 3
- **Comprehensive Coverage**: Medication management, lifestyle recommendations, monitoring
- **Multiple Output Formats**: JSON API responses with detailed care instructions

### Example Care Plan Structure
```json
{
  "care_plan": {
    "patient_summary": "Patient overview and current condition",
    "care_goals": ["Goal 1", "Goal 2"],
    "medication_management": ["Instruction 1", "Instruction 2"],
    "lifestyle_recommendations": ["Recommendation 1"],
    "monitoring_schedule": ["Schedule item 1"],
    "warning_signs": ["Sign 1", "Sign 2"],
    "follow_up_recommendations": ["Follow-up 1"]
  }
}
```

##  Monitoring & Observability

### Health Checks
- **Application Health**: `/health` endpoint with service status
- **Service Health**: Real-time monitoring of backend and frontend
- **Dependency Health**: AWS service connectivity

### Logging
- **Structured Logging**: JSON-formatted logs for production
- **Error Tracking**: Comprehensive error handling and reporting
- **Performance Metrics**: Response time and throughput monitoring

## 🔧 Development Workflow

### Code Quality
```bash
# Format code
poetry run black app/ tests/

# Sort imports
poetry run isort app/ tests/

# Run linting
poetry run flake8 app/ tests/
```

### Adding New Features
1. Create feature branch
2. Implement with tests
3. Update documentation
4. Run full test suite
5. Update version and changelog

## 🚀 Development Workflow

### Running Both Services
```bash
# Terminal 1: Start backend
cd ai-health-service
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Start frontend
cd ai-health-ui
npm start
```

### Environment Configuration
- **Backend**: Configure AWS credentials in `.env` file
- **Frontend**: Automatically connects to backend on localhost:8000
- **Development**: Hot reloading enabled for both services

## 📝 API Usage Examples

### File Upload
```bash
curl -X POST "http://localhost:8000/upload/pdf" \
  -F "file=@document.pdf" \
  -F "folder=medical-records"
```

### Care Plan Generation
```bash
curl -X POST "http://localhost:8000/care-plan/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_info": {
      "age": 45,
      "gender": "Female",
      "medical_conditions": ["Hypertension"]
    },
    "diagnosis": "Acute bronchitis",
    "prescriptions": [{
      "medication_name": "Azithromycin",
      "dosage": "500mg daily",
      "duration": "5 days"
    }]
  }'
```

## 🔗 Related Documentation

- [Care Plan Setup Guide](ai-health-service/CARE_PLAN_GUIDE.md) - Bedrock configuration
- [Poetry Migration Guide](ai-health-service/POETRY_MIGRATION.md) - Dependency management
- [S3 Access Configuration](ai-health-service/S3_ACCESS_FIX.md) - AWS setup

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Issues**: Create GitHub issues for bugs and feature requests
- **Discussions**: Use GitHub Discussions for questions and ideas

---

**Built with ❤️ for healthcare innovation**