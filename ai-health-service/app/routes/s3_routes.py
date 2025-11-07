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
        
        # If it's a JSON file, try to parse structured data directly
        if file_extension == "json":
            try:
                import json
                json_data = json.loads(extracted_text)
                
                # Extract patient info from JSON structure
                if isinstance(json_data, dict):
                    # Look for patient_info or similar structures
                    for key, value in json_data.items():
                        if "patient" in key.lower() and isinstance(value, dict):
                            if "age" in value:
                                patient_info["age"] = str(value["age"])
                            if "gender" in value:
                                patient_info["gender"] = str(value["gender"])
                            if "weight" in value:
                                patient_info["weight"] = str(value["weight"])
                            if "height" in value:
                                patient_info["height"] = str(value["height"])
                            if "bmi" in value:
                                patient_info["bmi"] = str(value["bmi"])
                        
                        # Extract vital signs from JSON
                        if "vital" in key.lower() and isinstance(value, dict):
                            for vital_key, vital_value in value.items():
                                vital_signs[vital_key] = str(vital_value)
                        
                        # Extract medications from JSON
                        if "prescription" in key.lower() or "medication" in key.lower():
                            if isinstance(value, list):
                                for med in value:
                                    if isinstance(med, dict):
                                        medications.append({
                                            "name": med.get("medication_name", med.get("name", "Unknown")),
                                            "medication_name": med.get("medication_name", med.get("name", "Unknown")),
                                            "dosage": med.get("dosage", "N/A"),
                                            "duration": med.get("duration", "As prescribed")
                                        })
                        
                        # Extract medical conditions from JSON
                        if "condition" in key.lower() or "diagnosis" in key.lower():
                            if isinstance(value, list):
                                medical_conditions.extend([str(cond) for cond in value])
                            elif isinstance(value, str):
                                medical_conditions.append(value)
            except:
                pass  # Fall back to NER and text parsing
        
        # Extract structured data from NER results
        if "ner_analysis" in result and "medical_entities" in result["ner_analysis"]:
            entities = result["ner_analysis"]["medical_entities"]
            
            for entity in entities:
                category = entity.get("category", "").upper()
                entity_type = entity.get("type", "").upper()
                text = entity.get("text", "")
                attributes = entity.get("attributes", [])
                
                if category == "MEDICAL_CONDITION":
                    medical_conditions.append(text)
                elif category == "MEDICATION":
                    # Extract dosage and frequency from attributes if available
                    dosage = "N/A"
                    frequency = "N/A"
                    
                    for attr in attributes:
                        attr_type = attr.get("Type", "").upper()
                        attr_text = attr.get("Text", "")
                        
                        if attr_type in ["DOSAGE", "STRENGTH"]:
                            dosage = attr_text
                        elif attr_type == "FREQUENCY":
                            frequency = attr_text
                    
                    medications.append({
                        "name": text,
                        "medication_name": text,
                        "dosage": f"{dosage} {frequency}".strip(),
                        "duration": "As prescribed",
                        "type": entity_type,
                        "confidence": entity.get("score", 0.0)
                    })
        
        # Extract PHI entities for patient demographics
        if "ner_analysis" in result and "phi_entities" in result["ner_analysis"]:
            phi_entities = result["ner_analysis"]["phi_entities"]
            
            for entity in phi_entities:
                category = entity.get("category", "").upper()
                entity_type = entity.get("type", "").upper()
                text = entity.get("text", "")
                
                if entity_type == "NAME":
                    if "name" not in patient_info:
                        patient_info["name"] = text
                elif entity_type == "AGE":
                    if "age" not in patient_info:
                        # Extract numeric age
                        import re
                        age_match = re.search(r'\d+', text)
                        if age_match:
                            patient_info["age"] = age_match.group()
        
        # Simple text parsing - extract basic information
        lines = extracted_text.split('\n')
        vital_signs = {}
        
        # Also check full text for patterns that might span lines
        full_text_lower = extracted_text.lower()
        
        # Extract patient info and vital signs
        for line in lines:
            line = line.strip()
            line_lower = line.lower()
            
            # Extract patient basic info
            if "patient:" in line_lower or "name:" in line_lower:
                try:
                    name = line.split(':', 1)[1].strip()
                    if name and not any(char.isdigit() for char in name):  # Avoid capturing IDs as names
                        patient_info["name"] = name
                except:
                    pass
            elif "age:" in line_lower or "years old" in line_lower or "y/o" in line_lower:
                try:
                    import re
                    # Try different age patterns
                    age_patterns = [
                        r'age:?\s*(\d+)',
                        r'(\d+)\s*years?\s*old',
                        r'(\d+)\s*y/?o',
                        r'age\s*(\d+)'
                    ]
                    
                    for pattern in age_patterns:
                        age_match = re.search(pattern, line_lower)
                        if age_match:
                            patient_info["age"] = age_match.group(1)
                            break
                except:
                    pass
            elif any(keyword in line_lower for keyword in ["gender:", "sex:", "male", "female", "m/f"]):
                try:
                    import re
                    # Try different gender patterns
                    gender_patterns = [
                        r'(?:gender|sex):?\s*(male|female|m|f)',
                        r'\b(male|female)\b',
                        r'm/f:?\s*(male|female|m|f)'
                    ]
                    
                    for pattern in gender_patterns:
                        gender_match = re.search(pattern, line_lower)
                        if gender_match:
                            gender_value = gender_match.group(1).lower()
                            if gender_value in ['m', 'male']:
                                patient_info["gender"] = "Male"
                            elif gender_value in ['f', 'female']:
                                patient_info["gender"] = "Female"
                            else:
                                patient_info["gender"] = gender_value.title()
                            break
                except:
                    pass
            elif "weight:" in line_lower or "wt:" in line_lower or "kg" in line_lower or "lbs" in line_lower:
                try:
                    import re
                    # Try different weight patterns
                    weight_patterns = [
                        r'weight:?\s*(\d+(?:\.\d+)?)\s*(kg|lbs?|pounds?)',
                        r'wt:?\s*(\d+(?:\.\d+)?)\s*(kg|lbs?|pounds?)',
                        r'(\d+(?:\.\d+)?)\s*(kg|lbs?|pounds?)',
                        r'weight:?\s*(\d+(?:\.\d+)?)'
                    ]
                    
                    for pattern in weight_patterns:
                        weight_match = re.search(pattern, line_lower)
                        if weight_match:
                            weight_value = weight_match.group(1)
                            weight_unit = weight_match.group(2) if len(weight_match.groups()) > 1 else "kg"
                            patient_info["weight"] = f"{weight_value} {weight_unit}"
                            vital_signs["weight"] = f"{weight_value} {weight_unit}"
                            break
                except:
                    pass
            elif "height:" in line_lower:
                try:
                    height_text = line.split(':', 1)[1].strip()
                    patient_info["height"] = height_text
                    vital_signs["height"] = height_text
                except:
                    pass
            elif "bmi:" in line_lower:
                try:
                    bmi_text = line.split(':', 1)[1].strip()
                    patient_info["bmi"] = bmi_text
                    vital_signs["bmi"] = bmi_text
                except:
                    pass
            
            # Extract vital signs
            elif "blood pressure:" in line_lower or "bp:" in line_lower:
                try:
                    bp_text = line.split(':', 1)[1].strip()
                    vital_signs["blood_pressure"] = bp_text
                except:
                    pass
            elif "heart rate:" in line_lower or "hr:" in line_lower or "pulse:" in line_lower:
                try:
                    hr_text = line.split(':', 1)[1].strip()
                    vital_signs["heart_rate"] = hr_text
                except:
                    pass
            elif "temperature:" in line_lower or "temp:" in line_lower:
                try:
                    temp_text = line.split(':', 1)[1].strip()
                    vital_signs["temperature"] = temp_text
                except:
                    pass
            elif "respiratory rate:" in line_lower or "rr:" in line_lower:
                try:
                    rr_text = line.split(':', 1)[1].strip()
                    vital_signs["respiratory_rate"] = rr_text
                except:
                    pass
            elif "oxygen saturation:" in line_lower or "o2 sat:" in line_lower or "spo2:" in line_lower:
                try:
                    o2_text = line.split(':', 1)[1].strip()
                    vital_signs["oxygen_saturation"] = o2_text
                except:
                    pass
        
        # Additional full-text pattern matching for demographics
        import re
        
        # If we haven't found age yet, try more patterns
        if "age" not in patient_info:
            age_patterns = [
                r'(\d+)\s*(?:year|yr)s?\s*old',
                r'age\s*(?:of\s*)?(?:is\s*)?(\d+)',
                r'(\d+)\s*y/?o\b',
                r'\b(\d+)\s*years?\b'
            ]
            for pattern in age_patterns:
                age_match = re.search(pattern, full_text_lower)
                if age_match:
                    age_val = int(age_match.group(1))
                    if 0 < age_val < 150:  # Reasonable age range
                        patient_info["age"] = str(age_val)
                        break
        
        # If we haven't found gender yet, try more patterns
        if "gender" not in patient_info:
            gender_patterns = [
                r'\b(male|female)\s*(?:patient|person|individual)',
                r'(?:patient|person|individual)\s*(?:is\s*)?(?:a\s*)?(male|female)',
                r'\b(male|female)\b(?!\s*(?:relative|family|parent))',
                r'gender\s*(?:is\s*)?(?::\s*)?(male|female|m|f)\b',
                r'sex\s*(?:is\s*)?(?::\s*)?(male|female|m|f)\b'
            ]
            for pattern in gender_patterns:
                gender_match = re.search(pattern, full_text_lower)
                if gender_match:
                    gender_value = gender_match.group(1).lower()
                    if gender_value in ['m', 'male']:
                        patient_info["gender"] = "Male"
                    elif gender_value in ['f', 'female']:
                        patient_info["gender"] = "Female"
                    break
        
        # If we haven't found weight yet, try more patterns
        if "weight" not in patient_info:
            weight_patterns = [
                r'weighs?\s*(\d+(?:\.\d+)?)\s*(kg|lbs?|pounds?)',
                r'weight\s*(?:of\s*)?(?:is\s*)?(\d+(?:\.\d+)?)\s*(kg|lbs?|pounds?)',
                r'(\d+(?:\.\d+)?)\s*(kg|kilograms?|lbs?|pounds?)\s*(?:weight|body\s*weight)',
                r'\b(\d+(?:\.\d+)?)\s*kg\b',
                r'\b(\d+(?:\.\d+)?)\s*(?:lbs?|pounds?)\b'
            ]
            for pattern in weight_patterns:
                weight_match = re.search(pattern, full_text_lower)
                if weight_match:
                    weight_value = weight_match.group(1)
                    weight_unit = weight_match.group(2) if len(weight_match.groups()) > 1 else "kg"
                    weight_val = float(weight_value)
                    # Reasonable weight range
                    if 20 < weight_val < 300:  
                        patient_info["weight"] = f"{weight_value} {weight_unit}"
                        vital_signs["weight"] = f"{weight_value} {weight_unit}"
                        break
        
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
            "vital_signs": vital_signs,
            "lab_results": {},
            "clinical_notes": result.get("extracted_text", ""),
            "raw_extraction": result
        }
                    
        logger.info(f"Successfully extracted medical data from {file_name}")
        
        return {
            "success": True,
            "message": "Medical data extracted successfully with enhanced demographics parsing",
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