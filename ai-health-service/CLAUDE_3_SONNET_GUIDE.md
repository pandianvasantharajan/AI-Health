# Claude 3 Sonnet Endpoint Documentation

## Overview

A new endpoint has been added for Claude 3 Sonnet, completing the full suite of Claude models available in the AI Health Service.

## New Claude 3 Sonnet Endpoint

### Model Configuration
- **Model ID:** `anthropic.claude-3-sonnet-20240229-v1:0`
- **Type:** Standard (Baseline)
- **Description:** Reliable and cost-effective baseline standard model
- **Access:** Direct model access (not inference profile)

### Endpoints

#### 1. Generate Care Plan with Claude 3 Sonnet
```
POST /care-plan/claude-3-sonnet
```

**Example Request:**
```bash
curl -X POST http://localhost:8000/care-plan/claude-3-sonnet \
  -H "Content-Type: application/json" \
  -d '{
    "patient_info": {
      "age": 55,
      "gender": "Male",
      "weight": 82.0,
      "medical_conditions": ["Type 2 Diabetes", "High cholesterol"],
      "allergies": ["Sulfa drugs"]
    },
    "diagnosis": "Bacterial pneumonia with comorbidities",
    "prescriptions": [
      {
        "medication_name": "Ceftriaxone",
        "dosage": "1g IV daily",
        "duration": "7 days",
        "instructions": "Administer over 30 minutes via IV infusion"
      },
      {
        "medication_name": "Prednisone",
        "dosage": "40mg daily for 5 days, then taper",
        "duration": "10 days total",
        "instructions": "Take with food to reduce stomach irritation"
      }
    ],
    "doctor_notes": "Patient admitted for IV antibiotics. Monitor blood glucose closely due to steroid use."
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Care plan generated successfully with Claude 3 Sonnet",
  "care_plan": {...},
  "model_used": "anthropic.claude-3-sonnet-20240229-v1:0",
  "diagnosis": "Bacterial pneumonia with comorbidities",
  "model_type": "Claude 3 Sonnet (Standard)"
}
```

#### 2. Sample Care Plan with Claude 3 Sonnet
```
POST /care-plan/claude-3-sonnet/sample
```

**Example Request:**
```bash
curl -X POST http://localhost:8000/care-plan/claude-3-sonnet/sample
```

**Sample Prescription Used:**
- **Patient:** 55-year-old male with Type 2 Diabetes and high cholesterol
- **Diagnosis:** Bacterial pneumonia with comorbidities
- **Medications:** Ceftriaxone IV, Prednisone taper, Albuterol nebulizer
- **Special Considerations:** Hospital admission, IV antibiotics, blood glucose monitoring

## Complete Model Lineup

The AI Health Service now supports **4 Claude models**:

| Model | Type | Endpoint | Model ID | Status |
|-------|------|----------|----------|--------|
| **Claude 4.5 Sonnet** | Premium | `/care-plan/generate` | `us.anthropic.claude-sonnet-4-5-20250929-v1:0` | Payment Required |
| **Claude 3.7 Sonnet** | Latest Standard | `/care-plan/claude-37-sonnet` | `us.anthropic.claude-3-7-sonnet-20250219-v1:0` | Payment Required |
| **Claude 3.5 Sonnet** | Standard | `/care-plan/claude-35-sonnet` | `us.anthropic.claude-3-5-sonnet-20241022-v2:0` | Payment Required |
| **Claude 3 Sonnet** | **Baseline Standard** | **`/care-plan/claude-3-sonnet`** | **`anthropic.claude-3-sonnet-20240229-v1:0`** | **Payment Required** |

## Updated Comparison Endpoint

The `/care-plan/compare` endpoint now tests all **4 models** simultaneously:

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
  "total_models": 4,
  "results": {
    "claude_4_5_sonnet": {...},
    "claude_3_7_sonnet": {...},
    "claude_3_5_sonnet": {...},
    "claude_3_sonnet": {...}
  },
  "comparison_notes": {
    "claude_4_5": "Premium model with enhanced capabilities (requires payment)",
    "claude_3_7": "Latest standard model with improved capabilities",
    "claude_3_5": "Standard model with proven performance",
    "claude_3": "Baseline standard model, reliable and cost-effective"
  }
}
```

## Model Positioning

### Claude 3 Sonnet Benefits
- **Cost-Effective:** Baseline pricing for standard Claude capabilities
- **Reliable:** Proven performance for healthcare applications
- **Accessibility:** Direct model access (not inference profile)
- **Foundation:** Good starting point for care plan generation

### Use Cases for Claude 3 Sonnet
1. **Development & Testing:** Cost-effective for initial development
2. **Basic Care Plans:** Suitable for routine, straightforward cases
3. **High Volume:** When cost per request is a primary concern
4. **Fallback Option:** Reliable backup when premium models unavailable

## Current Access Status

**All Claude models currently require payment method configuration:**

⚠️ **Payment Required:**
- Claude 4.5 Sonnet: Premium inference profile
- Claude 3.7 Sonnet: Latest standard inference profile  
- Claude 3.5 Sonnet: Standard inference profile
- **Claude 3 Sonnet: Direct model access**

**Resolution Steps:**
1. Add valid payment method in AWS Console
2. Configure billing for Bedrock services
3. Wait 15 minutes for activation
4. Test endpoints after activation

## API Reference

### Updated Models Endpoint
```
GET /care-plan/models
```

**Response includes Claude 3 Sonnet:**
```json
{
  "configured_models": {
    "claude_4_5_sonnet": {
      "model_id": "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
      "type": "Premium",
      "endpoint": "/care-plan/generate (default) or /care-plan/sample"
    },
    "claude_3_7_sonnet": {
      "model_id": "us.anthropic.claude-3-7-sonnet-20250219-v1:0",
      "type": "Latest Standard",
      "endpoint": "/care-plan/claude-37-sonnet or /care-plan/claude-37-sonnet/sample"
    },
    "claude_3_5_sonnet": {
      "model_id": "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
      "type": "Standard",
      "endpoint": "/care-plan/claude-35-sonnet or /care-plan/claude-35-sonnet/sample"
    },
    "claude_3_sonnet": {
      "model_id": "anthropic.claude-3-sonnet-20240229-v1:0",
      "type": "Standard",
      "endpoint": "/care-plan/claude-3-sonnet or /care-plan/claude-3-sonnet/sample"
    }
  }
}
```

### Health Check
```
GET /health
```

**Response shows all 4 models:**
```json
{
  "configured_models": {
    "claude_4_5_sonnet": "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
    "claude_3_7_sonnet": "us.anthropic.claude-3-7-sonnet-20250219-v1:0",
    "claude_3_5_sonnet": "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    "claude_3_sonnet": "anthropic.claude-3-sonnet-20240229-v1:0"
  }
}
```

## Testing Commands

### Basic Functionality Test
```bash
# Test endpoint structure
curl -X POST http://localhost:8000/care-plan/claude-3-sonnet/sample

# Test custom prescription
curl -X POST http://localhost:8000/care-plan/claude-3-sonnet \
  -H "Content-Type: application/json" \
  -d '{...prescription...}'

# Test all models comparison
curl -X POST http://localhost:8000/care-plan/compare \
  -H "Content-Type: application/json" \
  -d '{...prescription...}'
```

### Verification Commands
```bash
# Check model configuration
curl http://localhost:8000/health | jq '.configured_models'

# Check model details
curl http://localhost:8000/care-plan/models | jq '.configured_models'

# Check access status
curl http://localhost:8000/bedrock/access-check | jq '.detailed_results.model_access'
```

## Architecture Benefits

With Claude 3 Sonnet added, the service now provides:

1. **Complete Model Range:** From baseline to premium Claude capabilities
2. **Flexible Options:** Choice based on complexity, cost, and performance needs  
3. **Comprehensive Testing:** All models testable through comparison endpoint
4. **Scalable Architecture:** Easy to add future models following same pattern

The addition of Claude 3 Sonnet completes the Claude model lineup and provides a solid foundation model option for cost-effective care plan generation.