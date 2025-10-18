from mangum import Mangum
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app_vercel import app

# Create the ASGI handler for Vercel
handler = Mangum(app, lifespan="off")
