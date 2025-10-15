#!/bin/bash

# PhotoPro AI - Railway Deployment Startup Script
echo "🚀 Starting PhotoPro AI Backend..."

# Change to backend directory
cd backend

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Start the FastAPI application
echo "🌟 Starting FastAPI application..."
python3 main.py
