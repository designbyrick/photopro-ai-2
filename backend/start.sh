#!/bin/bash

# PhotoPro AI Backend Startup Script
echo "🚀 Starting PhotoPro AI Backend..."

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Run database migrations and setup
echo "🗄️ Setting up database..."
python3 scripts/setup_production.py

# Start the application
echo "🌟 Starting FastAPI application..."
exec gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
