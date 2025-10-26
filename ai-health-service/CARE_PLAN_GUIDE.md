# Care Plan Module Documentation

## Overview

The care plan module integrates with Amazon Bedrock to generate comprehensive care plans from doctor prescriptions. It uses AI to analyze prescriptions and create structured care plans with medication management, lifestyle recommendations, and monitoring schedules.

## Features

- **AI-Powered Care Plans**: Uses Amazon Bedrock (Claude 3 Sonnet) for intelligent care plan generation
- **Structured Input**: Accepts detailed prescription data with patient information
- **Comprehensive Output**: Generates care plans with multiple sections including:
  - Patient summary
  - Care goals
  - Medication management
  - Lifestyle recommendations
  - Monitoring schedule
  - Warning signs
  - Follow-up recommendations

## API Endpoints

### 1. Generate Care Plan from Prescription
**POST** `/care-plan/generate`

Generate a care plan from a doctor's prescription.

**Request Body:**
```json
{
  "patient_info": {
    "age": 45,
    "gender": "Female",
    "weight": 68.5,
    "medical_conditions": ["Hypertension", "Type 2 Diabetes"],
    "allergies": ["Penicillin"]
  },
  "diagnosis": "Acute bronchitis with underlying comorbidities",
  "prescriptions": [
    {
      "medication_name": "Amoxicillin-Clavulanate",
      "dosage": "875mg/125mg twice daily",
      "duration": "7 days",
      "instructions": "Take with food to reduce stomach upset"
    }
  ],
  "doctor_notes": "Monitor blood sugar levels during treatment"
}
```

### 2. Generate Sample Care Plan
**POST** `/care-plan/sample`

Generate a care plan using predefined sample data for testing.

### 3. List Available Models
**GET** `/care-plan/models`

List available Amazon Bedrock models for care plan generation.

## Amazon Bedrock Setup

### Required AWS Permissions

Your IAM user needs the following permissions for Bedrock:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:ListFoundationModels"
      ],
      "Resource": "*"
    }
  ]
}
```

### Enable Model Access

1. Go to AWS Console → Amazon Bedrock
2. Navigate to "Model access" in the left sidebar
3. Click "Manage model access"
4. Enable access to:
   - Anthropic Claude 3 Sonnet
   - Anthropic Claude 3 Haiku
   - Amazon Titan Text Express (optional)

### Configuration

Add to your `.env` file:
```env
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
BEDROCK_REGION=us-east-1
```

## Example Usage

### Using curl
```bash
# Test with sample data
curl -X POST "http://localhost:8000/care-plan/sample" \
     -H "accept: application/json"

# Generate custom care plan
curl -X POST "http://localhost:8000/care-plan/generate" \
     -H "accept: application/json" \
     -H "Content-Type: application/json" \
     -d '{
       "patient_info": {
         "age": 65,
         "gender": "Male",
         "medical_conditions": ["Heart Disease"]
       },
       "diagnosis": "Acute chest pain",
       "prescriptions": [
         {
           "medication_name": "Aspirin",
           "dosage": "81mg daily",
           "duration": "Ongoing",
           "instructions": "Take with food"
         }
       ]
     }'
```

### Using Python requests
```python
import requests

# Sample care plan
response = requests.post("http://localhost:8000/care-plan/sample")
care_plan = response.json()

print(f"Care Plan Generated: {care_plan['success']}")
print(f"Patient Summary: {care_plan['care_plan']['patient_summary']}")
```

## Response Format

The care plan response includes:

```json
{
  "success": true,
  "message": "Care plan generated successfully",
  "care_plan": {
    "patient_summary": "Brief overview of patient condition",
    "care_goals": ["Goal 1", "Goal 2"],
    "medication_management": [
      {
        "title": "Medication Schedule",
        "content": "Detailed instructions",
        "priority": "high"
      }
    ],
    "lifestyle_recommendations": [...],
    "monitoring_schedule": [...],
    "warning_signs": ["Sign 1", "Sign 2"],
    "follow_up_recommendations": [...],
    "generated_at": "2025-10-26T..."
  },
  "model_used": "anthropic.claude-3-sonnet-20240229-v1:0",
  "diagnosis": "Original diagnosis"
}
```

## Error Handling

Common errors and solutions:

1. **Access Denied to Bedrock**
   - Ensure IAM permissions are configured
   - Enable model access in Bedrock console

2. **Model Not Available**
   - Check if the model is enabled in your region
   - Use `/care-plan/models` to see available models

3. **Invalid Prescription Data**
   - Ensure all required fields are provided
   - Check data types match the schema

## Integration with File Upload

The care plan module works alongside the file upload module:

1. Upload prescription PDFs using `/upload/pdf`
2. Extract prescription data (manual or OCR)
3. Generate care plan using `/care-plan/generate`
4. Store both files and care plans in S3

## Security Considerations

- All AWS credentials should be properly secured
- Bedrock calls are logged for audit purposes
- Patient data should be handled according to HIPAA requirements
- Consider encryption for sensitive medical data

## Troubleshooting

### Bedrock Access Issues
```bash
# Test Bedrock access
aws bedrock list-foundation-models --region us-east-1

# Check IAM permissions
aws sts get-caller-identity
```

### Debug Mode
Set `DEBUG=True` in `.env` for detailed logging of Bedrock interactions.

## Model Comparison

| Model | Speed | Quality | Cost | Best For |
|-------|-------|---------|------|----------|
| Claude 3 Sonnet | Medium | High | Medium | Comprehensive care plans |
| Claude 3 Haiku | Fast | Good | Low | Quick assessments |
| Titan Text Express | Fast | Good | Low | Basic care plans |

Default: **Claude 3 Sonnet** for best balance of quality and performance.