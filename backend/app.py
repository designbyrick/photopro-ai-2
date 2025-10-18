#!/usr/bin/env python3
"""
PhotoPro AI - Main Entry Point for Railway Deployment
"""

import os
import uvicorn
from app import app

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    print(f"🚀 Starting PhotoPro AI on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)