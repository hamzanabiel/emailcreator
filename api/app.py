"""
FastAPI Application - Main Entry Point
Serves the web UI and provides REST API endpoints
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import logging

from api.routes import router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="CSV Email Tool",
    description="Web interface for generating Outlook email files from CSV data",
    version="1.0.0"
)

# Add CORS middleware (allows frontend to call API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api")

# Serve frontend static files
frontend_dir = Path(__file__).parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

@app.get("/")
async def root():
    """Serve the main frontend page"""
    frontend_file = frontend_dir / "index.html"
    if frontend_file.exists():
        return FileResponse(frontend_file)
    return {"message": "CSV Email Tool API", "status": "running"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "api": "running"
    }

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting CSV Email Tool Web Interface...")
    logger.info("Open your browser to: http://localhost:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
