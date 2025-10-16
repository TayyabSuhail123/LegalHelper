#!/bin/bash

# ContractCopilot Development Environment Setup Script

set -e

echo "🚀 Setting up ContractCopilot development environment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

# Check prerequisites
print_status "Checking prerequisites..."

# Check Node.js
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed. Please install Node.js 18+ and try again."
    exit 1
fi

NODE_VERSION=$(node --version | cut -d 'v' -f 2 | cut -d '.' -f 1)
if [ "$NODE_VERSION" -lt 18 ]; then
    print_error "Node.js version 18+ is required. Current version: $(node --version)"
    exit 1
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.11+ and try again."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d ' ' -f 2 | cut -d '.' -f 1,2)
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d '.' -f 1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d '.' -f 2)

if [ "$PYTHON_MAJOR" -lt 3 ] || [ "$PYTHON_MAJOR" -eq 3 -a "$PYTHON_MINOR" -lt 11 ]; then
    print_error "Python 3.11+ is required. Current version: $(python3 --version)"
    exit 1
fi

# Check UV (recommended) or fallback to pip
if command -v uv &> /dev/null; then
    print_status "UV found ✅ (recommended Python package manager)"
    USE_UV=true
else
    print_warning "UV not found. Installing UV for faster Python package management..."
    if command -v curl &> /dev/null; then
        curl -LsSf https://astral.sh/uv/install.sh | sh
        # Source the shell to get uv in PATH
        export PATH="$HOME/.cargo/bin:$PATH"
        if command -v uv &> /dev/null; then
            print_status "UV installed successfully ✅"
            USE_UV=true
        else
            print_warning "UV installation failed. Falling back to pip."
            USE_UV=false
        fi
    else
        print_warning "curl not found. Please install UV manually: https://docs.astral.sh/uv/getting-started/installation/"
        USE_UV=false
    fi
fi

print_status "Prerequisites check passed ✅"

# Install root dependencies
print_status "Installing root dependencies..."
npm install

# Setup backend
print_status "Setting up backend..."
cd backend

if [ "$USE_UV" = true ]; then
    print_status "Creating Python virtual environment with UV..."
    uv venv
    print_status "Installing dependencies with UV..."
    if [ -f "requirements.txt" ]; then
        uv pip install -r requirements.txt
        print_status "Installing development dependencies..."
        uv pip install -e ".[dev]" 2>/dev/null || print_warning "Development dependencies not available"
    else
        print_warning "requirements.txt not found in backend directory"
    fi
else
    if [ ! -d "venv" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    print_status "Activating virtual environment and installing dependencies..."
    source venv/bin/activate
    
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    else
        print_warning "requirements.txt not found in backend directory"
    fi
fi

cd ..

# Setup frontend
print_status "Setting up frontend..."
cd frontend

if [ -f "package.json" ]; then
    print_status "Installing frontend dependencies..."
    npm install
else
    print_warning "package.json not found in frontend directory"
fi

cd ..

# Create environment file template
print_status "Creating environment file template..."
if [ ! -f ".env" ]; then
    cat > .env << EOL
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Langfuse Configuration  
LANGFUSE_PUBLIC_KEY=your_langfuse_public_key_here
LANGFUSE_SECRET_KEY=your_langfuse_secret_key_here
LANGFUSE_HOST=https://cloud.langfuse.com

# Application Configuration
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# Frontend Configuration
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENVIRONMENT=development
EOL
    print_warning "Created .env file template. Please update with your actual API keys."
else
    print_status ".env file already exists"
fi

# Check Docker (optional)
if command -v docker &> /dev/null; then
    print_status "Docker found ✅"
    if command -v docker-compose &> /dev/null; then
        print_status "Docker Compose found ✅"
    else
        print_warning "Docker Compose not found. Install it for containerized development."
    fi
else
    print_warning "Docker not found. Install it for containerized development."
fi

print_status "🎉 Development environment setup complete!"
echo ""
echo "Next steps:"
echo "1. Update .env file with your API keys"
if [ "$USE_UV" = true ]; then
    echo "2. Run 'npm run dev' to start both frontend and backend (using UV)"
    echo "   Or run backend only: 'cd backend && uv run --with fastapi --with uvicorn[standard] --with pydantic-settings uvicorn main:app --reload'"
else
    echo "2. Run 'npm run dev' to start both frontend and backend"
    echo "   Or run backend only: 'cd backend && source venv/bin/activate && uvicorn main:app --reload'"
fi
echo "3. Visit http://localhost:3000 for the frontend"
echo "4. Visit http://localhost:8000/docs for API documentation"
echo ""
echo "For containerized development:"
echo "- Run 'docker-compose up -d' to start all services"
echo "- Run 'docker-compose down' to stop all services"
echo ""
if [ "$USE_UV" = true ]; then
    echo "🚀 You're using UV for faster Python package management!"
    echo "   Learn more: https://docs.astral.sh/uv/"
fi
