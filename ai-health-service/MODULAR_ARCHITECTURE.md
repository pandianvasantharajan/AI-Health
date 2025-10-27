# AI Health Service - Modular Architecture Guide

## Overview

The AI Health Service has been restructured into a modular architecture for better maintainability, scalability, and organization. Each feature area now has its own dedicated route module.

## New Architecture

### Directory Structure
```
app/
├── main.py                    # Main application entry point
├── config.py                  # Configuration settings
├── modules/                   # Business logic modules
│   ├── __init__.py
│   ├── file_upload.py         # S3 upload functionality
│   └── care_plan.py          # Bedrock AI integration
└── routes/                    # API route modules
    ├── __init__.py
    ├── s3_routes.py          # S3 file upload endpoints
    ├── care_plan_routes.py   # Care plan generation endpoints
    └── bedrock_routes.py     # Bedrock diagnostics endpoints
```

## Module Breakdown

### 1. S3 Routes (`/routes/s3_routes.py`)
**Prefix:** `/upload`
**Endpoints:**
- `POST /upload/pdf` - Upload PDF files with validation
- `POST /upload/file` - Upload any file type
- `GET /upload/file/{bucket_name}/{file_key:path}` - Get presigned URLs

### 2. Care Plan Routes (`/routes/care_plan_routes.py`)
**Prefix:** `/care-plan`
**Endpoints:**
- `POST /care-plan/generate` - Generate with Claude 4.5 Sonnet (default)
- `POST /care-plan/sample` - Sample data with Claude 4.5 Sonnet
- `POST /care-plan/claude-35-sonnet` - Generate with Claude 3.5 Sonnet
- `POST /care-plan/claude-35-sonnet/sample` - Sample data with Claude 3.5 Sonnet
- `POST /care-plan/claude-37-sonnet` - **NEW** Generate with Claude 3.7 Sonnet
- `POST /care-plan/claude-37-sonnet/sample` - **NEW** Sample data with Claude 3.7 Sonnet
- `POST /care-plan/compare` - Compare all three models side-by-side
- `GET /care-plan/models` - List available models
- `POST /care-plan/demo` - Demo structure without AI

### 3. Bedrock Routes (`/routes/bedrock_routes.py`)
**Prefix:** `/bedrock`
**Endpoints:**
- `GET /bedrock/access-check` - Comprehensive access diagnostics
- `GET /bedrock/permissions` - IAM permission analysis

## New Claude 3.7 Sonnet Integration

### Model Configuration
- **Model ID:** `us.anthropic.claude-3-7-sonnet-20250219-v1:0`
- **Type:** Latest Standard (Inference Profile)
- **Features:** Improved capabilities over Claude 3.5
- **Requirements:** Payment method (like other inference profiles)

### Sample Endpoint Test
```bash
curl -X POST http://localhost:8000/care-plan/claude-37-sonnet/sample
```

**Response:**
```json
{
  "success": true,
  "message": "Sample care plan generated successfully with Claude 3.7 Sonnet",
  "model_used": "us.anthropic.claude-3-7-sonnet-20250219-v1:0",
  "model_type": "Claude 3.7 Sonnet (Latest Standard)",
  "care_plan": {...},
  "sample_prescription": {...}
}
```

### Custom Endpoint Example
```bash
curl -X POST http://localhost:8000/care-plan/claude-37-sonnet \
  -H "Content-Type: application/json" \
  -d '{
    "patient_info": {
      "age": 32,
      "gender": "Male",
      "weight": 75.0,
      "medical_conditions": ["Mild asthma"],
      "allergies": ["Shellfish"]
    },
    "diagnosis": "Upper respiratory tract infection",
    "prescriptions": [
      {
        "medication_name": "Azithromycin",
        "dosage": "500mg on day 1, then 250mg daily",
        "duration": "5 days",
        "instructions": "Take on empty stomach"
      }
    ],
    "doctor_notes": "Patient has well-controlled asthma"
  }'
```

## Model Comparison

### Updated Comparison Endpoint
The `/care-plan/compare` endpoint now tests all three models:

```bash
curl -X POST http://localhost:8000/care-plan/compare \
  -H "Content-Type: application/json" \
  -d '{...prescription_data...}'
```

**Response Structure:**
```json
{
  "success": false,
  "message": "Care plan comparison completed",
  "successful_models": 0,
  "total_models": 3,
  "results": {
    "claude_4_5_sonnet": {
      "success": false,
      "error": "Access denied (payment required)",
      "model_type": "Premium"
    },
    "claude_3_5_sonnet": {
      "success": false,
      "error": "Access denied (payment required)",
      "model_type": "Standard"
    },
    "claude_3_7_sonnet": {
      "success": false,
      "error": "Access denied (payment required)",
      "model_type": "Latest Standard"
    }
  },
  "comparison_notes": {
    "claude_4_5": "Premium model with enhanced capabilities (requires payment)",
    "claude_3_5": "Standard model with proven performance",
    "claude_3_7": "Latest standard model with improved capabilities"
  }
}
```

## Access Status

### Current Model Access
Based on the latest diagnostics:

✅ **Working Models:**
- `anthropic.claude-3-haiku-20240307-v1:0` (Standard)
- `anthropic.claude-3-sonnet-20240229-v1:0` (Standard)

⚠️ **Payment Required (Inference Profiles):**
- `us.anthropic.claude-3-5-sonnet-20241022-v2:0`
- `us.anthropic.claude-3-7-sonnet-20250219-v1:0`
- `us.anthropic.claude-sonnet-4-5-20250929-v1:0`

### Payment Method Resolution
All inference profile models (`us.anthropic.*`) require:
1. Valid payment method in AWS console
2. 15-minute activation period after adding payment method
3. Proper billing configuration

## Benefits of Modular Architecture

### 1. **Separation of Concerns**
- S3 functionality isolated from AI logic
- Bedrock diagnostics separate from care plan generation
- Each module has single responsibility

### 2. **Maintainability**
- Easier to locate and modify specific functionality
- Reduced file size and complexity
- Clear dependency management

### 3. **Scalability**
- Easy to add new model endpoints
- Simple to extend functionality within each area
- Better testing isolation

### 4. **Developer Experience**
- Cleaner imports and dependencies
- Logical code organization
- Easier debugging and troubleshooting

## Development Workflow

### Adding New Models
1. Update `.env` with new model ID
2. Add model to `config.py`
3. Create new endpoint in `care_plan_routes.py`
4. Update `models` endpoint response
5. Add to comparison endpoint

### Adding New Features
1. Create new route file in `/routes/`
2. Import and include router in `main.py`
3. Add appropriate dependencies
4. Update documentation

## Testing

### Health Check
```bash
curl http://localhost:8000/health
```

### Model Status
```bash
curl http://localhost:8000/care-plan/models
```

### Access Diagnostics
```bash
curl http://localhost:8000/bedrock/access-check
```

### Permission Check
```bash
curl http://localhost:8000/bedrock/permissions
```

## Migration Notes

- **Old `main.py`** saved as `main_old.py`
- **No breaking changes** to API endpoints
- **Same functionality** with better organization
- **Added Claude 3.7 Sonnet** support
- **Enhanced diagnostics** and error handling

The modular architecture provides a solid foundation for future enhancements while maintaining all existing functionality and adding the new Claude 3.7 Sonnet model support.