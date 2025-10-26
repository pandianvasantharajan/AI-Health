#!/bin/bash

# Docker deployment script for AI Health Service

set -e

echo "🐳 AI Health Service Docker Deployment"
echo "======================================"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose found"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "📄 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️ Please edit .env file with your AWS credentials before proceeding!"
    echo ""
    echo "Required environment variables:"
    echo "- AWS_ACCESS_KEY_ID"
    echo "- AWS_SECRET_ACCESS_KEY"
    echo "- S3_BUCKET_NAME"
    echo ""
    read -p "Press Enter when you have configured the .env file..."
fi

echo "🔨 Building Docker image..."
docker-compose build

echo "🚀 Starting services..."
docker-compose up -d

echo ""
echo "✅ Deployment complete!"
echo ""
echo "🌐 Service URLs:"
echo "- API: http://localhost:8000"
echo "- Health Check: http://localhost:8000/health"
echo "- API Documentation: http://localhost:8000/docs"
echo ""
echo "📊 Useful commands:"
echo "- View logs: docker-compose logs -f"
echo "- Stop service: docker-compose down"
echo "- Restart service: docker-compose restart"
echo "- View status: docker-compose ps"
echo ""
echo "🧪 Test the service:"
echo "curl http://localhost:8000/health"