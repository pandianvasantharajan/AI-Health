# AI Health Development Guide

## 🚀 Quick Start

### Prerequisites
- Python 3.8.1+ 
- Node.js 16+ and npm
- Poetry (for Python dependency management)
- AWS credentials configured

### Starting the Application

#### Option 1: Using the Setup Script
```bash
# From the root directory
./setup-dev.sh
```

#### Option 2: Manual Setup

**Backend (Terminal 1):**
```bash
cd ai-health-service

# Install dependencies
poetry install

# Set up environment variables
cp .env.example .env
# Edit .env with your AWS credentials

# Start the backend
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend (Terminal 2):**
```bash
cd ai-health-ui

# Install dependencies
npm install

# Start the React app
npm start
```

### Access Points
- **Backend API**: http://localhost:8000
- **Frontend UI**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### Available Features
- **File Upload**: S3 integration for document storage
- **AI Care Plans**: 5 foundation models including Amazon Nova Micro
- **Medical Forms**: Pre-filled patient data with medication scheduling
- **Medication Management**: Table-based scheduling system

### Development Notes
- Backend automatically reloads on code changes
- Frontend hot-reloads React components
- All Docker-related configurations have been removed
- Focus on local development workflow

### Testing
```bash
# Backend tests
cd ai-health-service
poetry run pytest

# Frontend tests
cd ai-health-ui
npm test
```

### API Endpoints
- `GET /health` - Service health check
- `POST /care-plan/nova-micro` - Nova Micro care plan generation
- `POST /care-plan/compare` - Compare all 5 models
- `POST /upload/pdf` - Upload PDF files
- `GET /care-plan/models` - List available models

### Environment Setup
1. Copy `.env.example` to `.env` in `ai-health-service`
2. Configure AWS credentials for Bedrock access
3. Ensure S3 bucket access for file uploads