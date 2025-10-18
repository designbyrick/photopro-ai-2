#!/bin/bash

# PhotoPro AI Backend Startup Script
echo "🚀 Starting PhotoPro AI Backend..."

# Install dependencies if needed
if [ -f "requirements.txt" ]; then
    echo "📦 Installing Python dependencies..."
    pip3 install -r requirements.txt
fi

# Start the application using Uvicorn directly with Railway PORT
echo "🌟 Starting FastAPI application with Uvicorn..."
exec python3 -m uvicorn app:app --host 0.0.0.0 --port $PORT
