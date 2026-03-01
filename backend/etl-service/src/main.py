"""Main FastAPI application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from .config import settings
from .api.routes import router

# Create upload directory
Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="ETL Service for importing financial data from CSV files",
    version="1.0.0"
)

# CORS middleware - SECURITY FIX: Use configured origins instead of wildcard
# Parse allowed origins from comma-separated string
allowed_origins = [origin.strip() for origin in settings.cors_allowed_origins.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],  # Explicit methods
    allow_headers=["Content-Type", "Authorization", "Accept"],  # Explicit headers
)

# Include routers
app.include_router(router, prefix="/api", tags=["etl"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": settings.app_name,
        "version": "1.0.0",
        "status": "running"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
