#!/bin/bash

# Enable error handling
set -e

echo "X-Booking Development Environment Setup"
echo "========================================"

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "Error: Poetry is not installed."
    echo "Please install Poetry: https://python-poetry.org/docs/#installation"
    exit 1
fi

echo "✓ Poetry found"

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "Error: npm is not installed."
    echo "Please install Node.js and npm: https://nodejs.org/"
    exit 1
fi

echo "✓ npm found"

# Install Python dependencies
echo ""
echo "Installing Python dependencies with Poetry..."
poetry install

# Install Node.js dependencies
echo ""
echo "Installing Node.js dependencies with npm..."
npm install

# Start the development server
echo ""
echo "Starting development server..."
echo "Press Ctrl+C to stop"
echo ""
npm run dev

# Check if environment exists
if ! conda env list | grep -q "^$ENV_NAME "; then
    echo "Environment $ENV_NAME does not exist. Creating it..."
    conda create -y -n "$ENV_NAME" python=3.9 || {
        echo "Failed to create environment $ENV_NAME"
        exit 1
    }
fi

# Activate the environment
# On Mac, we need to source the conda.sh script first
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate "$ENV_NAME" || {
    echo "Failed to activate environment $ENV_NAME"
    exit 1
}

# Install Python dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "Installing Python dependencies..."
    pip install -r requirements.txt || {
        echo "Failed to install Python dependencies"
        exit 1
    }
fi

# Check for package.json and install npm dependencies if needed
if [ -f "package.json" ]; then
    echo "Checking npm dependencies..."
    
    # Check if node_modules directory exists
    if [ ! -d "node_modules" ]; then
        echo "Installing npm dependencies..."
        npm install || {
            echo "Failed to install npm dependencies"
            exit 1
        }
    fi
fi

echo "Starting the application..."
npm start 