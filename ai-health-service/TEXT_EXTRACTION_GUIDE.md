# Text Extraction & NER Service

## Overview

The AI Health Service now includes a comprehensive text extraction and Named Entity Recognition (NER) service that can process various file types and extract medical information using AWS services.

## New Endpoints

### 1. **POST** `/extract/text-and-ner`
Extract text and perform NER analysis from uploaded files.

**Supported File Types:**
- PDF (uses AWS Textract with PyPDF2 fallback)
- Microsoft Word (.docx, .doc)
- JSON files
- Plain text files

**Request:**
```bash
curl -X POST "http://localhost:8000/extract/text-and-ner" \
  -F "file=@sample-document.pdf" \
  -F "include_ner=true"
```

**Response:**
```json
{
  "success": true,
  "message": "Text extraction and analysis completed successfully",
  "data": {
    "extracted_text": "Patient information and medical notes...",
    "file_type": "pdf",
    "text_length": 1250,
    "extraction_method": "AWS Textract (with PyPDF2 fallback)",
    "filename": "sample-document.pdf",
    "file_size_bytes": 156789,
    "content_type": "application/pdf",
    "ner_analysis": {
      "medical_entities": [...],
      "phi_entities": [...],
      "total_medical_entities": 15,
      "total_phi_entities": 5,
      "categories": ["MEDICAL_CONDITION", "MEDICATION", "ANATOMY"],
      "types": ["DX_NAME", "GENERIC_NAME", "SYSTEM_ORGAN_SITE"]
    }
  }
}
```

### 2. **POST** `/extract/text-only`
Extract text only from uploaded files (no NER analysis).

**Request:**
```bash
curl -X POST "http://localhost:8000/extract/text-only" \
  -F "file=@document.docx"
```

### 3. **POST** `/extract/ner-only`
Perform NER analysis on provided text.

**Request:**
```bash
curl -X POST "http://localhost:8000/extract/ner-only" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "text=Patient diagnosed with diabetes, prescribed metformin 500mg twice daily."
```

### 4. **GET** `/extract/supported-formats`
Get list of supported file formats and capabilities.

### 5. **POST** `/upload/extract-medical-data`
**New endpoint for UI integration** - extracts medical data from S3 uploaded files.

**Request:**
```json
{
  "file_url": "https://bucket.s3.amazonaws.com/uploads/file.pdf",
  "file_name": "medical-report.pdf"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Medical data extracted successfully",
  "data": {
    "patient_info": {},
    "diagnoses": [
      {
        "condition": "Hypertension",
        "type": "MEDICAL_CONDITION",
        "confidence": 0.95
      }
    ],
    "medications": [
      {
        "medication_name": "Lisinopril",
        "type": "GENERIC_NAME",
        "confidence": 0.98
      }
    ],
    "vital_signs": {},
    "lab_results": {},
    "clinical_notes": "Full extracted text...",
    "raw_extraction": {...}
  }
}
```

## AWS Services Used

### 1. **AWS Textract**
- **Purpose**: Extract text from PDF documents
- **Features**: 
  - Document text detection
  - Layout analysis
  - Form and table extraction capability
- **Fallback**: PyPDF2 library if Textract fails

### 2. **AWS Comprehend Medical**
- **Purpose**: Medical Named Entity Recognition
- **Features**:
  - Medical entity detection (conditions, medications, anatomy)
  - Personal Health Information (PHI) detection
  - Entity categorization and confidence scoring
  - Attribute extraction

### 3. **AWS S3**
- **Purpose**: File storage and retrieval
- **Integration**: Download files from S3 URLs for processing

## Required AWS Permissions

To use all features, your AWS user/role needs these permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "textract:DetectDocumentText",
        "textract:AnalyzeDocument"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "comprehendmedical:DetectEntitiesV2",
        "comprehendmedical:DetectPHI"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject"
      ],
      "Resource": "arn:aws:s3:::your-bucket-name/*"
    }
  ]
}
```

## Current Status

✅ **Text Extraction**: Working for all supported file types
✅ **File Upload Integration**: `/upload/extract-medical-data` endpoint added
❌ **NER Analysis**: Requires AWS Comprehend Medical permissions

### Permission Error Fix

If you see this error:
```
User: arn:aws:iam::339712840004:user/vasantharajan is not authorized to perform: comprehendmedical:DetectEntitiesV2
```

**Solution:**
1. Add Comprehend Medical permissions to your AWS user/role
2. Or use the service without NER by setting `include_ner=false`

## Dependencies Added

New Python packages installed:
- `python-docx==1.1.0` - Microsoft Word document processing
- `PyPDF2==3.0.1` - PDF text extraction fallback
- `botocore==1.34.0` - AWS service client

## File Size Limits

- **File Upload**: 10MB maximum
- **NER Analysis**: 20,000 characters maximum (AWS Limit)
- **Textract**: 10MB single document (AWS Limit)

## Usage Examples

### Upload and Extract from PDF
```bash
curl -X POST "http://localhost:8000/extract/text-and-ner" \
  -F "file=@medical-report.pdf" \
  -F "include_ner=true"
```

### Upload and Extract from Word Document
```bash
curl -X POST "http://localhost:8000/extract/text-only" \
  -F "file=@patient-notes.docx"
```

### Analyze Medical Text
```bash
curl -X POST "http://localhost:8000/extract/ner-only" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "text=Patient John Smith diagnosed with Type 2 Diabetes. Prescribed Metformin 1000mg twice daily."
```

### Test with Sample JSON Data
```bash
curl -X POST "http://localhost:8000/extract/text-and-ner" \
  -F "file=@sample-medical-documents.json" \
  -F "include_ner=false"
```

## Integration with AI Health UI

The service is now integrated with the existing UI workflow:

1. **Step 1**: Upload file via `/upload/file` endpoint
2. **Step 2**: Extract medical data via `/upload/extract-medical-data` endpoint  
3. **Step 3**: Generate care plan with extracted data

The UI components (`FileUploadStep.js` and `PreviewStep.js`) are already configured to use these endpoints.