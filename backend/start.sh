#!/bin/bash

# PhotoPro AI Backend Startup Script
echo "🚀 Starting PhotoPro AI Backend..."

# Install dependencies if needed
if [ -f "requirements.txt" ]; then
    echo "📦 Installing Python dependencies..."
    pip install -r requirements.txt
fi

# Start the application using main.py
echo "🌟 Starting FastAPI application..."
exec python main.py
