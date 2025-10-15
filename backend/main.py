#!/usr/bin/env python3
"""
PhotoPro AI - Main Entry Point
"""

import os
import sys
from app import app

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    print(f"🚀 Starting PhotoPro AI on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)