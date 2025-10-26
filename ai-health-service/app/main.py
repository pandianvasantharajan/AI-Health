from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from typing import Optional

from .config import settings
from .modules.file_upload import S3FileUploader

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI instance
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI Health Service - File Upload API"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_s3_uploader() -> S3FileUploader:
    """
    Dependency to get S3 uploader instance.
    """
    return S3FileUploader(
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
        region_name=settings.aws_region
    )


@app.get("/")
async def root():
    """
    Root endpoint.
    """
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "status": "healthy"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version
    }


@app.post("/upload/pdf")
async def upload_pdf(
    file: UploadFile = File(...),
    folder: Optional[str] = "uploads",
    s3_uploader: S3FileUploader = Depends(get_s3_uploader)
):
    """
    Upload a PDF file to S3.
    
    Args:
        file: The PDF file to upload
        folder: Optional folder prefix in S3 (default: "uploads")
        s3_uploader: S3 uploader dependency
    
    Returns:
        JSON response with upload details
    """
    try:
        # Validate that a file was uploaded
        if not file:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Upload file to S3
        result = await s3_uploader.upload_file(
            file=file,
            bucket_name=settings.s3_bucket_name,
            folder=folder,
            validate_pdf=True
        )
        
        return JSONResponse(
            status_code=200,
            content=result
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error in upload endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error occurred during file upload"
        )


@app.post("/upload/file")
async def upload_file(
    file: UploadFile = File(...),
    folder: Optional[str] = "uploads",
    s3_uploader: S3FileUploader = Depends(get_s3_uploader)
):
    """
    Upload any file to S3 (no PDF validation).
    
    Args:
        file: The file to upload
        folder: Optional folder prefix in S3 (default: "uploads")
        s3_uploader: S3 uploader dependency
    
    Returns:
        JSON response with upload details
    """
    try:
        # Validate that a file was uploaded
        if not file:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Upload file to S3 without PDF validation
        result = await s3_uploader.upload_file(
            file=file,
            bucket_name=settings.s3_bucket_name,
            folder=folder,
            validate_pdf=False
        )
        
        return JSONResponse(
            status_code=200,
            content=result
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error in upload endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error occurred during file upload"
        )


@app.get("/file/{bucket_name}/{file_key:path}")
async def get_file_url(
    bucket_name: str,
    file_key: str,
    expiration: Optional[int] = 3600,
    s3_uploader: S3FileUploader = Depends(get_s3_uploader)
):
    """
    Get a presigned URL for accessing a file in S3.
    
    Args:
        bucket_name: S3 bucket name
        file_key: S3 file key
        expiration: URL expiration time in seconds (default: 1 hour)
        s3_uploader: S3 uploader dependency
    
    Returns:
        JSON response with presigned URL
    """
    try:
        url = s3_uploader.get_file_url(
            bucket_name=bucket_name,
            file_key=file_key,
            expiration=expiration
        )
        
        return {
            "success": True,
            "presigned_url": url,
            "expiration_seconds": expiration
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_file_url endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error occurred while generating file URL"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )