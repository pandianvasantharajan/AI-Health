"""
S3 File Upload Routes

This module contains all endpoints related to S3 file upload functionality.
"""

from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from fastapi.responses import JSONResponse
import logging
from typing import Optional
from botocore.exceptions import ClientError

from ..config import settings
from ..modules.file_upload import S3FileUploader

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/upload", tags=["S3 File Upload"])


def get_s3_uploader() -> S3FileUploader:
    """
    Dependency to get S3 uploader instance.
    """
    return S3FileUploader(
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
        region_name=settings.aws_region
    )


@router.post("/pdf")
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


@router.post("/file")
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


@router.get("/file/{bucket_name}/{file_key:path}")
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


@router.post("/extract-medical-data")
async def extract_medical_data(
    request: dict,
    s3_uploader: S3FileUploader = Depends(get_s3_uploader)
):
    """
    Extract medical data from an uploaded file using AWS services.
    
    Args:
        request: Dictionary containing file_url and file_name
        
    Returns:
        JSON response with extracted medical data
    """
    try:
        file_url = request.get('file_url')
        file_name = request.get('file_name', 'medical-document')
        
        if not file_url:
            raise HTTPException(status_code=400, detail="file_url is required")
        
        # Import here to avoid circular imports
        from ..modules.text_extraction import AWSTextExtractor
        
        # Initialize text extractor
        extractor = AWSTextExtractor(
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region,
            aws_role_arn=settings.aws_role_arn
        )
        
        # Parse S3 URL to get bucket and key
        import re
        s3_pattern = r'https://([^.]+)\.s3\.amazonaws\.com/(.+)'
        match = re.match(s3_pattern, file_url)
        
        if not match:
            raise HTTPException(status_code=400, detail="Invalid S3 URL format")
        
        bucket_name = match.group(1)
        object_key = match.group(2)
        
        # Download file from S3 using boto3
        import boto3
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region
        )
        
        try:
            s3_response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
            file_content = s3_response['Body'].read()
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to download from S3: {str(e)}")
        file_extension = file_name.split('.')[-1].lower() if '.' in file_name else 'txt'
        
        # Extract text and perform NER
        result = await extractor.extract_and_analyze(
            file=file_content,
            file_type=file_extension,
            include_ner=True
        )
        
        # Format response to match UI expectations  
        medical_conditions = []
        medications = []
        patient_info = {}
        
        # Get extracted text
        extracted_text = result.get("extracted_text", "")
        
        # Extract structured data from NER results
        if "ner_analysis" in result and "medical_entities" in result["ner_analysis"]:
            entities = result["ner_analysis"]["medical_entities"]
            
            for entity in entities:
                category = entity.get("category", "").upper()
                entity_type = entity.get("type", "").upper()
                text = entity.get("text", "")
                
                if category == "MEDICAL_CONDITION":
                    medical_conditions.append(text)
                elif category == "MEDICATION":
                    medications.append({
                        "name": text,
                        "medication_name": text,
                        "dosage": "N/A",
                        "duration": "N/A",
                        "type": entity_type,
                        "confidence": entity.get("score", 0.0)
                    })
        
        # Simple text parsing - extract basic information
        lines = extracted_text.split('\n')
        
        # Extract patient info
        for line in lines:
            line = line.strip()
            if "Patient:" in line:
                try:
                    name = line.split('Patient:')[1].strip()
                    patient_info["name"] = name
                except:
                    pass
            elif "Age:" in line:
                try:
                    age = line.split('Age:')[1].strip().split()[0]
                    patient_info["age"] = age
                except:
                    pass
        
        # Extract medications - look for numbered lists with mg dosages
        for i, line in enumerate(lines):
            line = line.strip()
            if any(keyword in line.lower() for keyword in ['furosemide', 'metoprolol', 'lisinopril', 'metformin']):
                if 'mg' in line.lower():
                    try:
                        # Parse medication line like "1. Furosemide 40mg twice daily"
                        parts = line.split()
                        name = parts[1] if parts[0].endswith('.') else parts[0]
                        dosage_part = [p for p in parts if 'mg' in p.lower()]
                        frequency_part = [p for p in parts if p.lower() in ['daily', 'twice', 'once']]
                        
                        dosage = dosage_part[0] if dosage_part else "N/A"
                        frequency = ' '.join(frequency_part) if frequency_part else "As prescribed"
                        
                        medications.append({
                            "name": name,
                            "medication_name": name,
                            "dosage": f"{dosage} {frequency}",
                            "duration": "As prescribed"
                        })
                    except:
                        pass
        
        # Extract medical conditions from diagnosis section
        diagnosis_section = False
        for line in lines:
            line = line.strip()
            if "DIAGNOSIS:" in line.upper():
                diagnosis_section = True
                # Also extract from the same line
                if ":" in line:
                    diagnosis_text = line.split(':', 1)[1].strip()
                    if diagnosis_text and not diagnosis_text.isdigit():
                        medical_conditions.append(diagnosis_text)
            elif diagnosis_section and line.startswith(('1.', '2.', '3.', '4.', '5.')):
                # Extract numbered diagnosis items
                condition = line.split('.', 1)[1].strip()
                if condition:
                    medical_conditions.append(condition)
            elif diagnosis_section and line.startswith(('MEDICATIONS', 'VITAL', 'FOLLOW')):
                diagnosis_section = False
        
        # Format response to match expected structure
        medical_data = {
            "patient_info": patient_info,
            "medications": medications,
            "medical_conditions": medical_conditions,
            "diagnosis": extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text,
            "raw_text": extracted_text,
            "vital_signs": {},
            "lab_results": {},
            "clinical_notes": result.get("extracted_text", ""),
            "raw_extraction": result
        }
                    
        logger.info(f"Successfully extracted medical data from {file_name}")
        
        return {
            "success": True,
            "message": "Medical data extracted successfully",
            "data": medical_data
        }
        
    except ClientError as e:
        logger.error(f"S3 access error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Failed to access S3 file: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error extracting medical data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to extract medical data: {str(e)}"
        )