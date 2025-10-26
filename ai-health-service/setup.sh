#!/bin/bash

# Setup script for AI Health Service

echo "🚀 Setting up AI Health Service with Poetry..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

echo "✅ Python found: $(python3 --version)"

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "📦 Poetry not found. Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
    export PATH="$HOME/.local/bin:$PATH"
    
    # Check if installation was successful
    if ! command -v poetry &> /dev/null; then
        echo "❌ Failed to install Poetry. Please install manually:"
        echo "   curl -sSL https://install.python-poetry.org | python3 -"
        echo "   Then add Poetry to your PATH and run this script again."
        exit 1
    fi
fi

echo "✅ Poetry found: $(poetry --version)"

# Configure Poetry to create virtual environment in project directory
echo "🔧 Configuring Poetry..."
poetry config virtualenvs.in-project true

# Install dependencies
echo "📚 Installing dependencies with Poetry..."
poetry install

# Copy environment file
if [ ! -f ".env" ]; then
    echo "📄 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️ Please edit .env file with your AWS credentials and S3 bucket name!"
else
    echo "✅ .env file already exists"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your AWS credentials:"
echo "   - AWS_ACCESS_KEY_ID"
echo "   - AWS_SECRET_ACCESS_KEY"
echo "   - S3_BUCKET_NAME"
echo ""
echo "2. Activate the Poetry environment:"
echo "   poetry shell"
echo ""
echo "3. Start the service:"
echo "   poetry run python run.py"
echo "   # or"
echo "   poetry run uvicorn app.main:app --reload"
echo ""
echo "4. Open http://localhost:8000/docs for API documentation"
echo ""
echo "Additional Poetry commands:"
echo "  poetry add <package>     # Add a dependency"
echo "  poetry remove <package>  # Remove a dependency" 
echo "  poetry show              # List installed packages"
echo "  poetry update            # Update dependencies"