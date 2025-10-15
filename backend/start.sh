#!/bin/bash

# PhotoPro AI Backend Startup Script
echo "🚀 Starting PhotoPro AI Backend..."

# Install dependencies if needed
if [ -f "requirements.txt" ]; then
    echo "📦 Installing Python dependencies..."
    pip install -r requirements.txt
fi

# Start the application using Gunicorn
echo "🌟 Starting FastAPI application with Gunicorn..."
exec gunicorn -c gunicorn.conf.py app:app
