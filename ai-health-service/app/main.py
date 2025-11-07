"""
AI Health Service - Main Application

A comprehensive health service providing:
- S3 file upload functionality
- AI-powered care plan generation using multiple Claude models
- Bedrock access and permission diagnostics
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from .config import settings
from .routes import s3_routes, care_plan_routes, bedrock_routes, text_extraction_routes

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.debug else logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI Health Service - S3 uploads and AI-powered care plan generation",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(s3_routes.router)
app.include_router(care_plan_routes.router)
app.include_router(bedrock_routes.router)
app.include_router(text_extraction_routes.router)


@app.get("/")
async def root():
    """
    Root endpoint.
    """
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "status": "healthy",
        "features": [
            "S3 file upload",
            "AI care plan generation", 
            "Multiple Claude models",
            "Bedrock access diagnostics"
        ],
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "s3_upload": "/upload",
            "care_plans": "/care-plan",
            "bedrock_diagnostics": "/bedrock"
        }
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "configured_models": {
            "claude_4_5_sonnet": settings.bedrock_model_id,
            "claude_3_7_sonnet": settings.claude_37_sonnet_model_id,
            "claude_3_5_sonnet": settings.claude_35_sonnet_model_id,
            "claude_3_sonnet": settings.claude_3_sonnet_model_id,
            "nova_micro": settings.nova_micro_model_id
        },
        "aws_region": settings.aws_region,
        "bedrock_region": settings.effective_bedrock_region
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )