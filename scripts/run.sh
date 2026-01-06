#!/bin/bash
# Script to run the Tree API locally with prerequisite checks
# Supports: macOS, Ubuntu/Debian Linux

set -e

echo "🌳 Tree Management API - Startup Script"
echo "========================================"
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to print status
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $2"
    else
        echo -e "${RED}✗${NC} $2"
    fi
}

# Check prerequisites
echo "Checking prerequisites..."
echo ""

MISSING_DEPS=0

# Check Python
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    print_status 0 "Python 3 found (version $PYTHON_VERSION)"
    PYTHON_CMD="python3"
elif command_exists python; then
    PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
    print_status 0 "Python found (version $PYTHON_VERSION)"
    PYTHON_CMD="python"
else
    print_status 1 "Python not found"
    echo -e "${YELLOW}  Install: https://www.python.org/downloads/${NC}"
    MISSING_DEPS=1
fi

# Check pip
if command_exists pip3; then
    print_status 0 "pip3 found"
    PIP_CMD="pip3"
elif command_exists pip; then
    print_status 0 "pip found"
    PIP_CMD="pip"
else
    print_status 1 "pip not found"
    echo -e "${YELLOW}  Install: $PYTHON_CMD -m ensurepip --upgrade${NC}"
    MISSING_DEPS=1
fi

# Check curl (optional but useful)
if command_exists curl; then
    print_status 0 "curl found (for testing)"
else
    print_status 1 "curl not found (optional, but recommended for testing)"
    echo -e "${YELLOW}  Install: sudo apt-get install curl (Ubuntu) or brew install curl (macOS)${NC}"
fi

echo ""

# Exit if missing required dependencies
if [ $MISSING_DEPS -eq 1 ]; then
    echo -e "${RED}Missing required dependencies. Please install them and try again.${NC}"
    exit 1
fi

echo "All prerequisites met!"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    $PYTHON_CMD -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies if needed
if ! pip show fastapi > /dev/null 2>&1; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

# Set default environment variables
export STORAGE_TYPE=${STORAGE_TYPE:-local}
export STORAGE_PATH=${STORAGE_PATH:-data/trees.json}
export LOG_LEVEL=${LOG_LEVEL:-INFO}

echo ""
echo "Configuration:"
echo "  Storage Type: $STORAGE_TYPE"
echo "  Storage Path: $STORAGE_PATH"
echo "  Log Level: $LOG_LEVEL"
echo ""
echo "API will be available at:"
echo "  - API: http://localhost:8000"
echo "  - Docs: http://localhost:8000/docs"
echo "  - Health: http://localhost:8000/health"
echo ""
echo "Starting server..."
echo ""

# Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

