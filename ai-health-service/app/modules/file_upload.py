import boto3
import uuid
import os
from datetime import datetime
from typing import Optional
from fastapi import UploadFile, HTTPException
from botocore.exceptions import ClientError, NoCredentialsError
import logging

logger = logging.getLogger(__name__)


class S3FileUploader:
    """
    A class to handle file uploads to AWS S3.
    """
    
    def __init__(self, aws_access_key_id: Optional[str] = None, 
                 aws_secret_access_key: Optional[str] = None, 
                 region_name: str = "us-east-1"):
        """
        Initialize the S3 client.
        
        Args:
            aws_access_key_id: AWS access key ID
            aws_secret_access_key: AWS secret access key
            region_name: AWS region name
        """
        try:
            if aws_access_key_id and aws_secret_access_key:
                self.s3_client = boto3.client(
                    's3',
                    aws_access_key_id=aws_access_key_id,
                    aws_secret_access_key=aws_secret_access_key,
                    region_name=region_name
                )
            else:
                # Use default credentials (from environment, IAM role, etc.)
                self.s3_client = boto3.client('s3', region_name=region_name)
                
        except NoCredentialsError:
            logger.error("AWS credentials not found")
            raise HTTPException(
                status_code=500, 
                detail="AWS credentials not configured"
            )
    
    def generate_file_key(self, original_filename: str, folder: str = "uploads") -> str:
        """
        Generate a unique file key for S3.
        
        Args:
            original_filename: The original filename
            folder: The folder prefix in S3
            
        Returns:
            A unique file key
        """
        # Get file extension
        file_extension = os.path.splitext(original_filename)[1]
        
        # Generate unique filename with timestamp and UUID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        
        filename = f"{timestamp}_{unique_id}{file_extension}"
        
        return f"{folder}/{filename}"
    
    def validate_pdf_file(self, file: UploadFile) -> bool:
        """
        Validate if the uploaded file is a PDF.
        
        Args:
            file: The uploaded file
            
        Returns:
            True if valid PDF, False otherwise
        """
        # Check content type
        if file.content_type not in ["application/pdf"]:
            return False
        
        # Check file extension
        if not file.filename.lower().endswith('.pdf'):
            return False
        
        return True
    
    async def upload_file(self, file: UploadFile, bucket_name: str, 
                         folder: str = "uploads", validate_pdf: bool = True) -> dict:
        """
        Upload a file to S3.
        
        Args:
            file: The file to upload
            bucket_name: S3 bucket name
            folder: Folder prefix in S3
            validate_pdf: Whether to validate PDF format
            
        Returns:
            Dictionary with upload details
        """
        try:
            # Validate file if required
            if validate_pdf and not self.validate_pdf_file(file):
                raise HTTPException(
                    status_code=400,
                    detail="Only PDF files are allowed"
                )
            
            # Generate unique file key
            file_key = self.generate_file_key(file.filename, folder)
            
            # Read file content
            file_content = await file.read()
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=bucket_name,
                Key=file_key,
                Body=file_content,
                ContentType=file.content_type,
                Metadata={
                    'original_filename': file.filename,
                    'upload_timestamp': datetime.now().isoformat(),
                    'file_size': str(len(file_content))
                }
            )
            
            # Generate file URL
            file_url = f"https://{bucket_name}.s3.amazonaws.com/{file_key}"
            
            logger.info(f"File uploaded successfully: {file_key}")
            
            return {
                "success": True,
                "message": "File uploaded successfully",
                "file_key": file_key,
                "file_url": file_url,
                "original_filename": file.filename,
                "file_size": len(file_content),
                "bucket_name": bucket_name
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            logger.error(f"AWS S3 error: {error_code} - {str(e)}")
            
            if error_code == 'NoSuchBucket':
                raise HTTPException(
                    status_code=404,
                    detail=f"S3 bucket '{bucket_name}' not found"
                )
            elif error_code == 'AccessDenied':
                raise HTTPException(
                    status_code=403,
                    detail="Access denied to S3 bucket"
                )
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to upload file to S3: {str(e)}"
                )
                
        except Exception as e:
            logger.error(f"Unexpected error during file upload: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"An unexpected error occurred: {str(e)}"
            )
    
    def get_file_url(self, bucket_name: str, file_key: str, expiration: int = 3600) -> str:
        """
        Generate a presigned URL for accessing a file in S3.
        
        Args:
            bucket_name: S3 bucket name
            file_key: S3 file key
            expiration: URL expiration time in seconds (default: 1 hour)
            
        Returns:
            Presigned URL string
        """
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket_name, 'Key': file_key},
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            logger.error(f"Error generating presigned URL: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to generate file access URL"
            )