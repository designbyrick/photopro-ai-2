import sys
from pathlib import Path

# Add parent directory to path so we can import from backend
sys.path.insert(0, str(Path(__file__).parent.parent))

from mangum import Mangum
from backend.app import app

# Vercel serverless handler
handler = Mangum(app, lifespan="off")