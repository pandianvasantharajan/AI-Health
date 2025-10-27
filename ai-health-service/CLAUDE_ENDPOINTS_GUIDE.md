# Claude Model Endpoints Guide

## Overview

The AI Health Service now supports both Claude 4.5 Sonnet and Claude 3.5 Sonnet models for care plan generation. This guide outlines all available endpoints and their usage.

## Available Models

### Claude 4.5 Sonnet (Premium Model)
- **Model ID**: `us.anthropic.claude-sonnet-4-5-20250929-v1:0`
- **Type**: Premium inference profile
- **Description**: Latest premium model with enhanced capabilities
- **Requirements**: AWS payment method configured

### Claude 3.5 Sonnet (Standard Model)
- **Model ID**: `us.anthropic.claude-3-5-sonnet-20241022-v2:0`
- **Type**: Standard inference profile
- **Description**: Proven standard model with reliable performance
- **Requirements**: Standard AWS access

## Endpoints

### 1. Claude 4.5 Sonnet Endpoints

#### Generate Care Plan (Default)
```bash
POST /care-plan/generate
```
- Uses Claude 4.5 Sonnet by default
- Accepts custom prescription data
- Returns structured care plan

**Example:**
```bash
curl -X POST http://localhost:8000/care-plan/generate \
  -H "Content-Type: application/json" \
  -d '{
    "patient_info": {
      "age": 45,
      "gender": "Female",
      "weight": 68.5,
      "medical_conditions": ["Hypertension"],
      "allergies": ["Penicillin"]
    },
    "diagnosis": "Acute bronchitis",
    "prescriptions": [
      {
        "medication_name": "Amoxicillin-Clavulanate",
        "dosage": "875mg/125mg twice daily",
        "duration": "7 days",
        "instructions": "Take with food"
      }
    ],
    "doctor_notes": "Monitor symptoms"
  }'
```

#### Sample Care Plan (Claude 4.5)
```bash
POST /care-plan/sample
```
- Uses Claude 4.5 Sonnet with predefined sample data
- Good for testing the premium model

### 2. Claude 3.5 Sonnet Endpoints

#### Generate Care Plan (Claude 3.5)
```bash
POST /care-plan/claude-35-sonnet
```
- Uses Claude 3.5 Sonnet specifically
- Accepts custom prescription data
- Returns structured care plan

**Example:**
```bash
curl -X POST http://localhost:8000/care-plan/claude-35-sonnet \
  -H "Content-Type: application/json" \
  -d '{
    "patient_info": {
      "age": 35,
      "gender": "Male",
      "weight": 70.0,
      "medical_conditions": [],
      "allergies": []
    },
    "diagnosis": "Common cold",
    "prescriptions": [
      {
        "medication_name": "Acetaminophen",
        "dosage": "500mg every 6 hours",
        "duration": "5 days",
        "instructions": "Take with food"
      }
    ],
    "doctor_notes": "Rest and hydration"
  }'
```

#### Sample Care Plan (Claude 3.5)
```bash
POST /care-plan/claude-35-sonnet/sample
```
- Uses Claude 3.5 Sonnet with predefined sample data
- Good for testing the standard model

### 3. Comparison Endpoint

#### Compare Both Models
```bash
POST /care-plan/compare
```
- Generates care plans using both Claude 4.5 and Claude 3.5
- Shows side-by-side comparison
- Handles failures gracefully for individual models

**Example:**
```bash
curl -X POST http://localhost:8000/care-plan/compare \
  -H "Content-Type: application/json" \
  -d '{
    "patient_info": {
      "age": 40,
      "gender": "Female",
      "weight": 65.0,
      "medical_conditions": ["Diabetes"],
      "allergies": []
    },
    "diagnosis": "Upper respiratory infection",
    "prescriptions": [
      {
        "medication_name": "Azithromycin",
        "dosage": "250mg daily",
        "duration": "5 days",
        "instructions": "Take on empty stomach"
      }
    ],
    "doctor_notes": "Follow up if symptoms persist"
  }'
```

### 4. Model Information

#### List Available Models
```bash
GET /care-plan/models
```
- Shows all available Bedrock models
- Displays configured models with details
- Includes endpoint information

### 5. Demo Endpoint

#### Demo Care Plan Structure
```bash
POST /care-plan/demo
```
- Shows expected care plan structure without calling Bedrock
- Useful for understanding the data format
- Does not require AWS credentials

## Response Format

All care plan endpoints return a structured response:

```json
{
  "success": true,
  "message": "Care plan generated successfully",
  "care_plan": {
    "patient_summary": "...",
    "care_goals": ["..."],
    "medication_management": [
      {
        "title": "...",
        "content": "...",
        "priority": "high|medium|low"
      }
    ],
    "lifestyle_recommendations": [...],
    "monitoring_schedule": [...],
    "warning_signs": [...],
    "follow_up_recommendations": [...]
  },
  "model_used": "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
  "diagnosis": "...",
  "model_type": "Claude 4.5 Sonnet (Premium)"
}
```

## Error Handling

Common error responses:

1. **Access Denied**: AWS IAM permissions or payment method issues
2. **Invalid Model ID**: Model not available or incorrect inference profile
3. **Validation Error**: Invalid request parameters
4. **Rate Limiting**: API rate limits exceeded

## Configuration

Models are configured in `.env`:

```env
# Claude 4.5 Sonnet (Premium)
BEDROCK_MODEL_ID=us.anthropic.claude-sonnet-4-5-20250929-v1:0

# Claude 3.5 Sonnet (Standard)
CLAUDE_35_SONNET_MODEL_ID=us.anthropic.claude-3-5-sonnet-20241022-v2:0
```

## Testing

1. Start the service: `docker-compose up -d`
2. Check health: `curl http://localhost:8000/health`
3. Test models endpoint: `curl http://localhost:8000/care-plan/models`
4. Test demo endpoint: `curl -X POST http://localhost:8000/care-plan/demo`
5. Test comparison: Use the `/care-plan/compare` endpoint

## Notes

- Both models require inference profiles (use `us.` prefix)
- Claude 4.5 requires payment method configuration
- Claude 3.5 is available with standard AWS access
- The comparison endpoint helps evaluate model differences
- All endpoints support the same prescription data format