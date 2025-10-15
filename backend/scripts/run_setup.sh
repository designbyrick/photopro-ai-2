#!/bin/bash

# PhotoPro AI Production Setup Script
# This script sets up the production environment

echo "🚀 PhotoPro AI Production Setup"
echo "================================"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

# Check if we're in the backend directory
if [ ! -f "main.py" ]; then
    echo "❌ Please run this script from the backend directory"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Run the setup script
echo "🔧 Running production setup..."
python3 scripts/setup_production.py

# Check if setup was successful
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Production setup completed successfully!"
    echo ""
    echo "🚀 You can now start the application with:"
    echo "   gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000"
    echo ""
    echo "📚 API Documentation will be available at: /docs"
    echo "🔍 Health check endpoint: /health"
else
    echo ""
    echo "❌ Production setup failed!"
    echo "Please check the error messages above and fix the issues."
    exit 1
fi
