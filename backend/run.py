"""Simple script to run the FastAPI server."""
import os
import sys
from pathlib import Path
import uvicorn

# Change to backend directory to ensure .env file is found
BACKEND_DIR = Path(__file__).parent
os.chdir(BACKEND_DIR)
sys.path.insert(0, str(BACKEND_DIR))

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

