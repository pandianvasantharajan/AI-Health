# AI-Health Monorepo

This is a monorepo containing the AI Health application components.

## Projects

### 1. ai-health-service (Python)
A Python FastAPI service that provides file upload functionality to AWS S3. Uses Poetry for dependency management.

### 2. ai-health-ui (React) - Coming Soon
A React frontend application for interacting with the AI Health service.

## Quick Start with Docker 🐳

The fastest way to get started is using Docker:

### Prerequisites
- Docker and Docker Compose installed
- AWS S3 bucket created
- AWS credentials ready

### 1. Clone and Navigate
```bash
git clone <your-repo-url>
cd AI-Health
```

### 2. Configure Environment
```bash
cd ai-health-service
cp .env.example .env
# Edit .env file with your AWS credentials and S3 bucket name
```

### 3. Run with Docker Compose
```bash
docker-compose up --build
```

### 4. Access the Service
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Alternative Setup Methods

### Local Development
Each project has its own README with specific setup instructions for local development.

### Manual Docker Build
```bash
cd ai-health-service
docker build -t ai-health-service .
docker run -p 8000:8000 --env-file .env ai-health-service
```

## Project Structure

```
AI-Health/
├── ai-health-service/          # Python FastAPI service
│   ├── app/                    # Application code
│   ├── Dockerfile              # Docker configuration
│   ├── docker-compose.yml      # Docker Compose setup
│   ├── requirements.txt        # Python dependencies
│   └── README.md              # Service-specific documentation
├── ai-health-ui/              # React frontend (future)
└── README.md                  # This file
```

## API Endpoints

Once running, the service provides these main endpoints:

- `POST /upload/pdf` - Upload PDF files to S3
- `POST /upload/file` - Upload any file to S3
- `GET /file/{bucket_name}/{file_key}` - Get presigned URLs
- `GET /health` - Service health check

## Environment Configuration

Required environment variables in `.env`:

```env
AWS_ACCESS_KEY_ID=your_aws_access_key_id
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-s3-bucket-name
```