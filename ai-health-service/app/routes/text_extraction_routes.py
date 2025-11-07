"""
Text Extraction Routes

This module contains endpoints for text extraction and NER analysis
from various file types using AWS services.
"""

from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, Form
from fastapi.responses import JSONResponse
import logging
from typing import Optional, Dict, Any
import mimetypes
import os

from ..config import settings
from ..modules.text_extraction import AWSTextExtractor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/extract", tags=["Text Extraction & NER"])


def get_text_extractor() -> AWSTextExtractor:
    """
    Dependency to get AWS Text Extractor instance.
    """
    return AWSTextExtractor(
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
        region_name=settings.aws_region,
        aws_role_arn=settings.aws_role_arn
    )


def get_file_type(file: UploadFile) -> str:
    """
    Determine file type from filename or content type.
    """
    filename = file.filename.lower() if file.filename else ""
    content_type = file.content_type or ""
    
    # Check by file extension
    if filename.endswith('.pdf'):
        return 'pdf'
    elif filename.endswith(('.docx', '.doc')):
        return 'docx'
    elif filename.endswith('.json'):
        return 'json'
    elif filename.endswith('.txt'):
        return 'txt'
    
    # Check by content type
    if 'pdf' in content_type:
        return 'pdf'
    elif 'word' in content_type or 'document' in content_type:
        return 'docx'
    elif 'json' in content_type:
        return 'json'
    elif 'text' in content_type:
        return 'txt'
    
    # Default to text if unknown
    return 'txt'


@router.post("/text-and-ner")
async def extract_text_and_ner(
    file: UploadFile = File(...),
    include_ner: bool = Form(default=True),
    extractor: AWSTextExtractor = Depends(get_text_extractor)
):
    """
    Extract text and perform NER analysis from uploaded file.
    
    Supported file types:
    - PDF: Uses AWS Textract (with PyPDF2 fallback)
    - Word (DOC/DOCX): Uses python-docx
    - JSON: Direct parsing
    - TXT: Plain text reading
    
    Args:
        file: Uploaded file (PDF, Word, JSON, or TXT)
        include_ner: Whether to include Named Entity Recognition
        
    Returns:
        JSON response with extracted text and NER analysis
    """
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Determine file type
        file_type = get_file_type(file)
        
        # Check file size (limit to 10MB)
        content = await file.read()
        file_size = len(content)
        
        if file_size > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(
                status_code=413, 
                detail="File size too large. Maximum size is 10MB."
            )
        
        logger.info(f"Processing file: {file.filename}, type: {file_type}, size: {file_size} bytes")
        
        # Extract text and perform NER using the content bytes
        result = await extractor.extract_and_analyze(
            file=content,
            file_type=file_type,
            include_ner=include_ner
        )
        
        # Add metadata
        result.update({
            "filename": file.filename,
            "file_size_bytes": file_size,
            "content_type": file.content_type
        })
        
        logger.info(f"Successfully processed {file.filename}")
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Text extraction and analysis completed successfully",
                "data": result
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing file {file.filename}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process file: {str(e)}"
        )


@router.post("/text-only")
async def extract_text_only(
    file: UploadFile = File(...),
    extractor: AWSTextExtractor = Depends(get_text_extractor)
):
    """
    Extract text only from uploaded file (no NER analysis).
    
    Args:
        file: Uploaded file (PDF, Word, JSON, or TXT)
        
    Returns:
        JSON response with extracted text only
    """
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Determine file type
        file_type = get_file_type(file)
        
        # Check file size (limit to 10MB)
        content = await file.read()
        file_size = len(content)
        
        if file_size > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(
                status_code=413, 
                detail="File size too large. Maximum size is 10MB."
            )
        
        logger.info(f"Extracting text from: {file.filename}, type: {file_type}")
        
        # Extract text only using the content bytes
        result = await extractor.extract_and_analyze(
            file=content,
            file_type=file_type,
            include_ner=False
        )
        
        # Add metadata
        result.update({
            "filename": file.filename,
            "file_size_bytes": file_size,
            "content_type": file.content_type
        })
        
        logger.info(f"Successfully extracted text from {file.filename}")
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Text extraction completed successfully",
                "data": result
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error extracting text from {file.filename}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to extract text: {str(e)}"
        )


@router.post("/ner-only")
async def analyze_ner_only(
    text: str = Form(...),
    extractor: AWSTextExtractor = Depends(get_text_extractor)
):
    """
    Perform NER analysis on provided text.
    
    Args:
        text: Text content to analyze
        
    Returns:
        JSON response with NER analysis results
    """
    try:
        # Validate text
        if not text or not text.strip():
            raise HTTPException(status_code=400, detail="No text provided")
        
        if len(text) > 20000:
            raise HTTPException(
                status_code=413,
                detail="Text too long. Maximum length is 20,000 characters."
            )
        
        logger.info(f"Performing NER analysis on text (length: {len(text)} chars)")
        
        # Perform NER analysis
        ner_results = await extractor._perform_ner(text)
        
        result = {
            "text_length": len(text),
            "ner_analysis": ner_results
        }
        
        logger.info("NER analysis completed successfully")
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "NER analysis completed successfully",
                "data": result
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in NER analysis: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"NER analysis failed: {str(e)}"
        )


@router.get("/supported-formats")
async def get_supported_formats():
    """
    Get list of supported file formats and extraction methods.
    
    Returns:
        JSON response with supported formats
    """
    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "message": "Supported file formats",
            "data": {
                "supported_formats": [
                    {
                        "format": "PDF",
                        "extensions": [".pdf"],
                        "extraction_method": "AWS Textract (with PyPDF2 fallback)",
                        "features": ["Text extraction", "NER analysis"]
                    },
                    {
                        "format": "Microsoft Word",
                        "extensions": [".docx", ".doc"],
                        "extraction_method": "python-docx",
                        "features": ["Text extraction", "NER analysis"]
                    },
                    {
                        "format": "JSON",
                        "extensions": [".json"],
                        "extraction_method": "JSON parser",
                        "features": ["Text extraction", "NER analysis"]
                    },
                    {
                        "format": "Plain Text",
                        "extensions": [".txt"],
                        "extraction_method": "Plain text reader",
                        "features": ["Text extraction", "NER analysis"]
                    }
                ],
                "ner_capabilities": [
                    "Medical entity recognition",
                    "Personal Health Information (PHI) detection",
                    "Entity categorization and scoring",
                    "Attribute extraction"
                ],
                "limits": {
                    "max_file_size": "10MB",
                    "max_text_length_for_ner": "20,000 characters"
                }
            }
        }
    )