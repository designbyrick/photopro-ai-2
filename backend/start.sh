#!/bin/bash

# PhotoPro AI Backend Startup Script
echo "🚀 Starting PhotoPro AI Backend..."

# Install dependencies if needed
if [ -f "requirements.txt" ]; then
    echo "📦 Installing Python dependencies..."
    pip install -r requirements.txt
fi

# Start the application using Uvicorn directly
echo "🌟 Starting FastAPI application..."
exec python -m uvicorn app:app --host 0.0.0.0 --port 8080
