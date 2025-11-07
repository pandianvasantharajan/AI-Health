#!/bin/bash

# AI Health Service - Docker Development Setup Script
# This script sets up and runs the development environment using Docker

echo "🏥 AI Health Service - Docker Development Setup"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "./docker-compose.dev.yml" ]; then
    print_error "Please run this script from the AI-Health root directory"
    exit 1
fi

# Check if Docker and Docker Compose are available
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker and try again."
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose and try again."
    exit 1
fi

print_status "Starting AI Health Service with Docker..."

# Stop any existing containers
print_status "Stopping any existing containers..."
docker-compose -f docker-compose.dev.yml down

# Build and start services
print_status "Building and starting development containers..."
docker-compose -f docker-compose.dev.yml up --build -d

# Wait for services to be ready
print_status "Waiting for services to be ready..."
sleep 15

# Check backend health
print_status "Checking backend service health..."
for i in {1..10}; do
    if curl -s http://localhost:8000/health | grep -q "healthy"; then
        print_success "Backend service is running and healthy!"
        break
    else
        if [ $i -eq 10 ]; then
            print_error "Backend service failed to start properly"
            print_status "Showing backend logs:"
            docker-compose -f docker-compose.dev.yml logs ai-health-service
            exit 1
        else
            print_status "Waiting for backend... (attempt $i/10)"
            sleep 3
        fi
    fi
done

# Check frontend
print_status "Checking frontend service..."
if curl -s http://localhost:3000 &> /dev/null; then
    print_success "Frontend service is running!"
else
    print_warning "Frontend service may still be starting..."
fi

# Display status
echo
echo "🎉 Docker Development Environment Ready!"
echo "======================================="
echo
print_success "Backend Service: http://localhost:8000"
print_success "Frontend UI: http://localhost:3000"
echo
echo "📚 Available Endpoints:"
echo "  • Health Check: http://localhost:8000/health"
echo "  • API Docs: http://localhost:8000/docs"
echo "  • Bedrock Access Check: http://localhost:8000/bedrock/access-check"
echo "  • Upload Medical Data: POST /upload/extract-medical-data"
echo
echo "🔥 Hot Reload Features:"
echo "  • Backend: Changes in ./ai-health-service/ will auto-reload FastAPI"
echo "  • Frontend: Changes in ./ai-health-ui/src/ will auto-reload React"
echo
echo "🧪 Test Commands:"
echo "  • Backend Health: curl http://localhost:8000/health"
echo "  • View Logs: docker-compose -f docker-compose.dev.yml logs -f"
echo "  • Backend Logs: docker-compose -f docker-compose.dev.yml logs -f ai-health-service"
echo "  • Frontend Logs: docker-compose -f docker-compose.dev.yml logs -f ai-health-ui"
echo
echo "🛑 To Stop Services:"
echo "  • docker-compose -f docker-compose.dev.yml down"
echo
echo "🌐 Open http://localhost:3000 in your browser to use the AI Health Care Plan Generator!"
echo
echo "📝 Development Tips:"
echo "  • Edit files in ./ai-health-service/ and see changes instantly"
echo "  • Edit files in ./ai-health-ui/src/ and see changes in browser"
echo "  • View real-time logs: docker-compose -f docker-compose.dev.yml logs -f"