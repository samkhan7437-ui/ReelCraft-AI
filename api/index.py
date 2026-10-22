import sys
import os
from pathlib import Path

# Set Vercel environment flag
os.environ["VERCEL"] = "1"

# Add project root to sys.path so 'app' imports resolve cleanly
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Ensure writable ephemeral output directories exist in /tmp
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "/tmp/output"))
for sub in ["audio", "videos", "images"]:
    (OUTPUT_DIR / sub).mkdir(parents=True, exist_ok=True)

# Import the FastAPI application
from app.main import app

# Vercel serverless entrypoint
handler = app
