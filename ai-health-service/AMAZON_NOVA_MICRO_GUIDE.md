# Amazon Nova Micro Endpoint Documentation

## Overview

The AI Health Service now includes Amazon Nova Micro - a fast, cost-effective text generation model that provides excellent care plan generation based on medical factors. This endpoint completes the comprehensive model lineup with Amazon's latest foundation model.

## Amazon Nova Micro Integration

### Model Configuration
- **Model ID:** `amazon.nova-micro-v1:0`
- **Type:** Amazon Nova (Text Generation)
- **Description:** Fast, cost-effective text generation model
- **Focus:** Medical factors-based care planning
- **Access:** Direct model access

### Key Features
- **Cost-Effective:** Optimized for high-volume use cases
- **Fast Response:** Quick inference times for efficient workflows
- **Medical Factors Focus:** Specialized for complex medical condition analysis
- **Comprehensive Coverage:** Multi-comorbidity care plan generation

## Endpoints

### 1. Generate Care Plan with Nova Micro
```
POST /care-plan/nova-micro
```

**Example Request:**
```bash
curl -X POST http://localhost:8000/care-plan/nova-micro \
  -H "Content-Type: application/json" \
  -d '{
    "patient_info": {
      "age": 35,
      "gender": "Female",
      "weight": 65.0,
      "medical_conditions": ["Asthma"],
      "allergies": ["Sulfa drugs"]
    },
    "diagnosis": "Asthma exacerbation",
    "prescriptions": [
      {
        "medication_name": "Prednisone",
        "dosage": "40mg daily",
        "duration": "5 days",
        "instructions": "Take with food, taper as directed"
      }
    ],
    "doctor_notes": "Patient responds well to oral steroids"
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Care plan generated successfully with Amazon Nova Micro",
  "care_plan": {
    "summary": "Comprehensive care plan for asthma exacerbation management",
    "treatment_plan": [...],
    "medication_management": [...],
    "lifestyle_recommendations": [...],
    "follow_up_recommendations": [...]
  },
  "diagnosis": "Asthma exacerbation",
  "model_used": "amazon.nova-micro-v1:0",
  "model_type": "Amazon Nova Micro"
}
```

### 2. Sample Care Plan with Medical Factors Focus
```
POST /care-plan/nova-micro/sample
```

**Example Request:**
```bash
curl -X POST http://localhost:8000/care-plan/nova-micro/sample
```

**Sample Medical Case:**
- **Patient:** 65-year-old female with multiple comorbidities
- **Primary Conditions:** Heart Failure, Diabetes, Hypertension, CKD Stage 3
- **Diagnosis:** Acute exacerbation of chronic heart failure with reduced ejection fraction
- **Complexity:** High - multiple medical factors requiring careful coordination

**Response Includes:**
```json
{
  "success": true,
  "message": "Sample care plan generated successfully with Amazon Nova Micro",
  "care_plan": {...},
  "sample_prescription": {...},
  "model_used": "amazon.nova-micro-v1:0",
  "model_type": "Amazon Nova Micro",
  "medical_factors_focus": {
    "primary_conditions": ["Heart Failure", "Diabetes", "Hypertension", "CKD"],
    "key_considerations": ["Fluid management", "Kidney function monitoring", "Drug interactions"],
    "complexity_level": "High - multiple comorbidities requiring careful coordination"
  }
}
```

## Complete Model Ecosystem

The AI Health Service now supports **5 foundation models**:

| Model | Type | Specialty | Model ID | Endpoint |
|-------|------|-----------|----------|----------|
| **Claude 4.5 Sonnet** | Premium | Advanced AI | `us.anthropic.claude-sonnet-4-5-20250929-v1:0` | `/care-plan/generate` |
| **Claude 3.7 Sonnet** | Latest Standard | Enhanced Performance | `us.anthropic.claude-3-7-sonnet-20250219-v1:0` | `/care-plan/claude-37-sonnet` |
| **Claude 3.5 Sonnet** | Standard | Proven Performance | `us.anthropic.claude-3-5-sonnet-20241022-v2:0` | `/care-plan/claude-35-sonnet` |
| **Claude 3 Sonnet** | Baseline Standard | Cost-Effective | `anthropic.claude-3-sonnet-20240229-v1:0` | `/care-plan/claude-3-sonnet` |
| **Amazon Nova Micro** | **Amazon Nova** | **Medical Factors** | **`amazon.nova-micro-v1:0`** | **`/care-plan/nova-micro`** |

## Medical Factors Specialization

### What Makes Nova Micro Special for Healthcare?

1. **Multi-Comorbidity Analysis**
   - Handles complex cases with multiple medical conditions
   - Considers drug interactions and contraindications
   - Optimizes treatment for competing priorities

2. **Cost-Effective Care Planning**
   - Fast inference for high-volume healthcare workflows
   - Efficient processing for routine care plan generation
   - Optimal for telemedicine and urgent care scenarios

3. **Medical Factor Integration**
   - Age-specific considerations
   - Gender-based medical differences
   - Weight-adjusted dosing recommendations
   - Allergy and contraindication management

### Sample Medical Factors Analysis

The Nova Micro sample endpoint demonstrates handling of:

**Primary Conditions:**
- Heart Failure (fluid management)
- Type 2 Diabetes (glucose monitoring)
- Hypertension (blood pressure control)
- Chronic Kidney Disease (medication adjustments)

**Key Medical Considerations:**
- **Fluid Management:** Critical in heart failure patients
- **Kidney Function Monitoring:** Essential for medication safety
- **Drug Interactions:** Multiple medications require careful coordination
- **Contraindication Awareness:** Avoiding harmful drug combinations

## Updated Comparison Testing

The `/care-plan/compare` endpoint now tests **all 5 models**:

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
  "successful_models": 1,
  "total_models": 5,
  "results": {
    "claude_4_5_sonnet": {...},
    "claude_3_7_sonnet": {...},
    "claude_3_5_sonnet": {...},
    "claude_3_sonnet": {...},
    "nova_micro": {...}
  },
  "comparison_notes": {
    "claude_4_5": "Premium model with enhanced capabilities (requires payment)",
    "claude_3_7": "Latest standard model with improved capabilities",
    "claude_3_5": "Standard model with proven performance", 
    "claude_3": "Baseline standard model, reliable and cost-effective",
    "nova_micro": "Amazon Nova Micro - Fast, cost-effective text generation"
  }
}
```

## Technical Implementation

### Request Format for Nova Micro
```json
{
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "text": "care_plan_prompt"
        }
      ]
    }
  ],
  "inferenceConfig": {
    "max_new_tokens": 4000,
    "temperature": 0.3,
    "top_p": 0.9
  }
}
```

### Response Format from Nova Micro
```json
{
  "output": {
    "message": {
      "content": [
        {
          "text": "generated_care_plan_json"
        }
      ]
    }
  }
}
```

## Access Status

**Current Status for Nova Micro:**
- ✅ **Model Available:** `amazon.nova-micro-v1:0` accessible
- ✅ **Direct Access:** No inference profile required
- ✅ **Regional Support:** Available in `us-east-1`
- ⚠️ **Payment Required:** Like other Bedrock models, requires valid payment method

## Use Cases for Nova Micro

### 1. High-Volume Healthcare Workflows
- **Urgent Care Centers:** Quick care plan generation
- **Telemedicine Platforms:** Cost-effective consultations
- **Hospital Systems:** Bulk care plan processing

### 2. Complex Medical Cases
- **Multi-Comorbidity Patients:** Multiple condition management
- **Elderly Care:** Age-specific considerations
- **Chronic Disease Management:** Long-term care coordination

### 3. Medical Education
- **Training Scenarios:** Complex case studies
- **Clinical Decision Support:** Evidence-based recommendations
- **Research Applications:** Medical factor analysis

## API Reference

### Updated Models Endpoint
```
GET /care-plan/models
```

**Response includes Nova Micro:**
```json
{
  "configured_models": {
    "nova_micro": {
      "model_id": "amazon.nova-micro-v1:0",
      "type": "Amazon Nova",
      "description": "Amazon Nova Micro - Fast, cost-effective text generation model",
      "endpoint": "/care-plan/nova-micro or /care-plan/nova-micro/sample"
    }
  }
}
```

### Health Check Endpoint
```
GET /health
```

**Response shows all 5 models:**
```json
{
  "status": "healthy",
  "configured_models": {
    "claude_4_5_sonnet": "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
    "claude_3_7_sonnet": "us.anthropic.claude-3-7-sonnet-20250219-v1:0",
    "claude_3_5_sonnet": "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    "claude_3_sonnet": "anthropic.claude-3-sonnet-20240229-v1:0",
    "nova_micro": "amazon.nova-micro-v1:0"
  }
}
```

## Testing Commands

### Basic Functionality Tests
```bash
# Test Nova Micro sample endpoint
curl -X POST http://localhost:8000/care-plan/nova-micro/sample

# Test Nova Micro with custom prescription
curl -X POST http://localhost:8000/care-plan/nova-micro \
  -H "Content-Type: application/json" \
  -d '{...prescription...}'

# Test all 5 models comparison
curl -X POST http://localhost:8000/care-plan/compare \
  -H "Content-Type: application/json" \
  -d '{...prescription...}'
```

### Verification Commands
```bash
# Check Nova Micro configuration
curl http://localhost:8000/health | jq '.configured_models.nova_micro'

# Check all model details
curl http://localhost:8000/care-plan/models | jq '.configured_models.nova_micro'

# Check access status including Nova Micro
curl http://localhost:8000/bedrock/access-check | jq '.detailed_results.model_access."amazon.nova-micro-v1:0"'
```

## Medical Factors Benefits

### Enhanced Medical Decision Support
1. **Drug Interaction Checking:** Comprehensive medication analysis
2. **Contraindication Awareness:** Safety-first prescribing
3. **Age-Appropriate Dosing:** Patient-specific recommendations
4. **Comorbidity Management:** Holistic care approach

### Cost-Effective Healthcare AI
1. **High-Volume Processing:** Efficient for healthcare systems
2. **Quick Turnaround:** Fast response times for urgent care
3. **Scalable Solution:** Handles varying workload demands
4. **Resource Optimization:** Cost-effective AI deployment

## Architecture Excellence

With Amazon Nova Micro, the AI Health Service provides:

1. **Complete Model Portfolio:** 5 models covering all use cases and budgets
2. **Medical Specialization:** Dedicated medical factors analysis
3. **Flexible Deployment:** From premium to cost-effective options
4. **Comprehensive Testing:** All models testable through comparison endpoint
5. **Future-Ready Architecture:** Easy integration of new models

Amazon Nova Micro completes the comprehensive AI health ecosystem, providing specialized medical factors analysis with cost-effective, fast performance for healthcare workflows requiring complex multi-comorbidity care plan generation.