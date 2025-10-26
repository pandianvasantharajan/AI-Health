# AI Health Service

A FastAPI-based service for uploading files to AWS S3, specifically designed for handling PDF documents in the AI Health ecosystem.

## Features

- **PDF Upload**: Dedicated endpoint for PDF file uploads with validation
- **Generic File Upload**: Support for uploading any file type
- **S3 Integration**: Secure file storage using AWS S3
- **File URL Generation**: Generate presigned URLs for secure file access
- **Input Validation**: Comprehensive file validation and error handling
- **RESTful API**: Clean, well-documented REST endpoints

## Prerequisites

- Python 3.8+
- Poetry (Python dependency management)
- AWS Account with S3 access
- AWS credentials configured

## Installation

### Option 1: Docker (Recommended) 🐳

**Prerequisites:**
- Docker and Docker Compose installed
- AWS S3 bucket created
- AWS credentials

**Quick Start:**
```bash
# 1. Clone and navigate
git clone <repository-url>
cd AI-Health/ai-health-service

# 2. Configure environment
cp .env.example .env
# Edit .env file with your AWS credentials

# 3. Run with Docker Compose
docker-compose up --build

# 4. Access the service
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

**One-Click Deployment Script:**
```bash
# Use the automated deployment script
./deploy-docker.sh
```
This script will:
- Check Docker installation
- Create .env file if needed
- Build and start the service
- Provide useful management commands

**Manual Docker Build:**
```bash
# Build the image
docker build -t ai-health-service .

# Run the container
docker run -p 8000:8000 --env-file .env ai-health-service

# Or run with environment variables directly
docker run -p 8000:8000 \
  -e AWS_ACCESS_KEY_ID=your_key \
  -e AWS_SECRET_ACCESS_KEY=your_secret \
  -e AWS_REGION=us-east-1 \
  -e S3_BUCKET_NAME=your-bucket \
  ai-health-service
```

### Option 2: Local Development with Poetry

1. **Clone the repository** (if not already done):
   ```bash
   git clone <repository-url>
   cd AI-Health/ai-health-service
   ```

2. **Install Poetry** (if not already installed):
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   # Add Poetry to PATH (follow the instructions shown after installation)
   ```

3. **Run the setup script**:
   ```bash
   ./setup.sh
   ```

4. **Or manual setup**:
   ```bash
   # Install dependencies with Poetry
   poetry install
   
   # Set up environment
   cp .env.example .env
   # Edit .env file with your AWS credentials
   ```

## Usage

### Starting the Server

#### With Docker (Recommended)
```bash
# Using Docker Compose (recommended)
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop the service
docker-compose down
```

#### Local Development with Poetry
**Development mode**:
```bash
# Activate Poetry environment
poetry shell

# Run the application
poetry run python run.py

# Or start with uvicorn directly
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`

### API Documentation

Once the server is running, visit:
- **Interactive API docs**: http://localhost:8000/docs
- **ReDoc documentation**: http://localhost:8000/redoc

## API Endpoints

### Health Check

- **GET** `/` - Welcome message and service info
- **GET** `/health` - Health check endpoint

### File Upload

#### Upload PDF File
- **POST** `/upload/pdf`
- **Parameters**:
  - `file`: PDF file to upload (required)
  - `folder`: S3 folder prefix (optional, default: "uploads")
- **Response**:
  ```json
  {
    "success": true,
    "message": "File uploaded successfully",
    "file_key": "uploads/20241025_123456_abc12345.pdf",
    "file_url": "https://your-bucket.s3.amazonaws.com/uploads/20241025_123456_abc12345.pdf",
    "original_filename": "document.pdf",
    "file_size": 1024567,
    "bucket_name": "your-bucket"
  }
  ```

#### Upload Any File
- **POST** `/upload/file`
- **Parameters**:
  - `file`: Any file to upload (required)
  - `folder`: S3 folder prefix (optional, default: "uploads")
- **Response**: Same as PDF upload

#### Get File URL
- **GET** `/file/{bucket_name}/{file_key:path}`
- **Parameters**:
  - `bucket_name`: S3 bucket name
  - `file_key`: S3 file key/path
  - `expiration`: URL expiration in seconds (optional, default: 3600)
- **Response**:
  ```json
  {
    "success": true,
    "presigned_url": "https://...",
    "expiration_seconds": 3600
  }
  ```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `AWS_ACCESS_KEY_ID` | AWS Access Key ID | None |
| `AWS_SECRET_ACCESS_KEY` | AWS Secret Access Key | None |
| `AWS_REGION` | AWS Region | us-east-1 |
| `S3_BUCKET_NAME` | S3 Bucket Name | Required |
| `APP_NAME` | Application Name | AI Health Service |
| `APP_VERSION` | Application Version | 1.0.0 |
| `DEBUG` | Debug Mode | True |

### AWS Credentials

You can provide AWS credentials in several ways:

1. **Environment variables** (recommended for development):
   ```env
   AWS_ACCESS_KEY_ID=your_key
   AWS_SECRET_ACCESS_KEY=your_secret
   ```

2. **AWS Credentials file** (`~/.aws/credentials`):
   ```ini
   [default]
   aws_access_key_id = your_key
   aws_secret_access_key = your_secret
   ```

3. **IAM Roles** (recommended for production/EC2)

## Example Usage

### Upload a PDF using curl

```bash
curl -X POST "http://localhost:8000/upload/pdf" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@document.pdf" \
     -F "folder=documents"
```

### Upload using Python requests

```python
import requests

url = "http://localhost:8000/upload/pdf"
files = {"file": ("document.pdf", open("document.pdf", "rb"), "application/pdf")}
data = {"folder": "documents"}

response = requests.post(url, files=files, data=data)
print(response.json())
```

## File Storage Structure

Files are stored in S3 with the following structure:
```
s3://your-bucket/
├── uploads/
│   ├── 20241025_123456_abc12345.pdf
│   ├── 20241025_134567_def67890.pdf
│   └── ...
├── documents/
│   └── ...
└── other-folders/
    └── ...
```

## Error Handling

The API provides comprehensive error handling with appropriate HTTP status codes:

- **400 Bad Request**: Invalid file format, missing file, etc.
- **403 Forbidden**: AWS access denied
- **404 Not Found**: S3 bucket not found
- **500 Internal Server Error**: Server errors, AWS configuration issues

## Development

### Project Structure

```
ai-health-service/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration settings
│   └── modules/
│       ├── __init__.py
│       └── file_upload.py   # S3 upload functionality
├── requirements.txt         # Python dependencies
├── run.py                  # Application entry point
├── .env.example           # Environment variables template
├── .gitignore            # Git ignore rules
└── README.md            # This file
```

### Adding New Features

1. Create new modules in the `app/modules/` directory
2. Add new endpoints in `app/main.py`
3. Update configuration in `app/config.py` if needed
4. Add new dependencies with Poetry: `poetry add <package-name>`
5. Update development dependencies: `poetry add --group dev <package-name>`

### Poetry Commands Reference

```bash
# Install dependencies
poetry install

# Add a new dependency
poetry add requests

# Add a development dependency
poetry add --group dev pytest

# Remove a dependency
poetry remove requests

# Update all dependencies
poetry update

# Show installed packages
poetry show

# Export requirements (if needed for compatibility)
poetry export -f requirements.txt --output requirements.txt

# Run commands in virtual environment
poetry run python script.py

# Activate shell
poetry shell
```

## Production Deployment

### Docker Production Deployment

**Using Docker Compose for Production:**
```bash
# Create production environment file
cp .env.example .env.prod
# Configure production values in .env.prod

# Run in production mode
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

**Kubernetes Deployment Example:**
```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-health-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ai-health-service
  template:
    metadata:
      labels:
        app: ai-health-service
    spec:
      containers:
      - name: ai-health-service
        image: ai-health-service:latest
        ports:
        - containerPort: 8000
        env:
        - name: AWS_ACCESS_KEY_ID
          valueFrom:
            secretKeyRef:
              name: aws-credentials
              key: access-key-id
        - name: AWS_SECRET_ACCESS_KEY
          valueFrom:
            secretKeyRef:
              name: aws-credentials
              key: secret-access-key
        - name: S3_BUCKET_NAME
          value: "your-production-bucket"
---
apiVersion: v1
kind: Service
metadata:
  name: ai-health-service
spec:
  selector:
    app: ai-health-service
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

### Traditional Production Deployment

For production deployment without Docker, consider:

1. **Use a production WSGI server** like Gunicorn
2. **Configure proper CORS** settings
3. **Use IAM roles** instead of access keys
4. **Enable logging** and monitoring
5. **Set up SSL/TLS** certificates
6. **Configure environment variables** securely
7. **Use a reverse proxy** like Nginx

Example production command:
```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker Best Practices for Production

1. **Use multi-stage builds** for smaller images
2. **Run as non-root user** (already implemented)
3. **Use specific image tags** instead of `latest`
4. **Set resource limits**:
   ```yaml
   deploy:
     resources:
       limits:
         memory: 512M
         cpus: '0.5'
   ```
5. **Enable health checks** (already implemented)
6. **Use secrets management** for sensitive data

## Docker Troubleshooting

### Common Issues and Solutions

**Container fails to start:**
```bash
# Check container logs
docker-compose logs ai-health-service

# Check if port is already in use
docker ps | grep 8000
```

**AWS credentials not working:**
```bash
# Verify environment variables are set
docker-compose exec ai-health-service env | grep AWS

# Test AWS connectivity
docker-compose exec ai-health-service python -c "import boto3; print(boto3.Session().get_available_regions('s3'))"
```

**Service not responding:**
```bash
# Check if container is running
docker-compose ps

# Check container health
docker inspect ai-health-service_ai-health-service_1 | grep Health -A 10

# Test connectivity
curl http://localhost:8000/health
```

### Docker Commands Reference

```bash
# Build and start
docker-compose up --build -d

# View logs (follow)
docker-compose logs -f

# Stop services
docker-compose down

# Restart specific service
docker-compose restart ai-health-service

# Check service status
docker-compose ps

# Access container shell
docker-compose exec ai-health-service bash

# View resource usage
docker stats

# Clean up unused images/containers
docker system prune -f
```

## License

This project is part of the AI-Health monorepo.