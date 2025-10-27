#!/bin/bash

# AI Health Service - Development Setup Script
# This script sets up and runs both the backend service and React UI

echo "🏥 AI Health Service - Development Setup"
echo "========================================"

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
if [ ! -f "./ai-health-service/docker-compose.yml" ]; then
    print_error "Please run this script from the AI-Health root directory"
    exit 1
fi

print_status "Starting AI Health Service setup..."

# Step 1: Start the backend service
print_status "Step 1: Starting AI Health Backend Service..."
cd ai-health-service

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Build and start the service
print_status "Building Docker image..."
docker-compose build

print_status "Starting backend service..."
docker-compose up -d

# Wait for service to be ready
print_status "Waiting for backend service to be ready..."
sleep 10

# Check if backend is healthy
if curl -s http://localhost:8000/health | grep -q "healthy"; then
    print_success "Backend service is running and healthy!"
else
    print_error "Backend service failed to start properly"
    exit 1
fi

# Step 2: Start the React UI
print_status "Step 2: Starting React UI..."
cd ../ai-health-ui

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    print_status "Installing React dependencies..."
    npm install
fi

print_status "Starting React development server..."
print_warning "The React server will start in a new terminal window/tab"

# Start React in the background
npm start &
REACT_PID=$!

# Wait for React to start
print_status "Waiting for React server to start..."
sleep 15

# Check if React is running
if curl -s http://localhost:3000 | grep -q "AI Health"; then
    print_success "React UI is running!"
else
    print_warning "React UI may still be starting..."
fi

# Display status
echo
echo "🎉 Setup Complete!"
echo "=================="
echo
print_success "Backend Service: http://localhost:8000"
print_success "React UI: http://localhost:3000"
echo
echo "📚 Available Endpoints:"
echo "  • Health Check: http://localhost:8000/health"
echo "  • API Docs: http://localhost:8000/docs"
echo "  • Nova Micro: POST /care-plan/nova-micro"
echo "  • All Models: POST /care-plan/compare"
echo
echo "🧪 Test Commands:"
echo "  • Backend Health: curl http://localhost:8000/health"
echo "  • Nova Micro Sample: curl -X POST http://localhost:8000/care-plan/nova-micro/sample"
echo
echo "🛑 To Stop Services:"
echo "  • Backend: cd ai-health-service && docker-compose down"
echo "  • React: Press Ctrl+C in the React terminal"
echo
echo "🌐 Open http://localhost:3000 in your browser to use the AI Health Care Plan Generator!"

# Keep the script running to show logs
print_status "Press Ctrl+C to stop monitoring..."
wait $REACT_PID