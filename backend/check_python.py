#!/usr/bin/env python3
"""
Python detection test for Railway
"""

import sys
import os

print("Python version:", sys.version)
print("Python executable:", sys.executable)
print("PATH:", os.environ.get('PATH', 'Not set'))
print("PORT:", os.environ.get('PORT', 'Not set'))

# Test if we can import required modules
try:
    import fastapi
    print("✅ FastAPI available")
except ImportError as e:
    print("❌ FastAPI not available:", e)

try:
    import gunicorn
    print("✅ Gunicorn available")
except ImportError as e:
    print("❌ Gunicorn not available:", e)

try:
    import uvicorn
    print("✅ Uvicorn available")
except ImportError as e:
    print("❌ Uvicorn not available:", e)

print("Python detection test complete!")
