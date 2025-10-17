#!/bin/bash

# ContractCopilot Backend Start Script

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Simple check - must be in backend directory
if [ ! -f "main.py" ]; then
    echo "❌ Please run this script from the backend directory"
    echo "Usage: cd backend && ./start.sh"
    exit 1
fi

print_status "Starting ContractCopilot backend..."

# Check if UV is available
if command -v uv &> /dev/null; then
    print_status "Starting with UV (fast mode)..."
    uv run --with fastapi --with "uvicorn[standard]" --with pydantic-settings uvicorn main:app --reload --host 0.0.0.0 --port 8000
else
    print_warning "UV not found. Please install UV for better performance."
    if [ -d ".venv" ]; then
        print_status "Starting with virtual environment..."
        source .venv/bin/activate && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
    else
        print_warning "No virtual environment found. Please run setup first."
        exit 1
    fi
fi
