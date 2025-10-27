# Bedrock Access & Permission Check Endpoints

## Overview

Two new diagnostic endpoints have been added to the AI Health Service to help troubleshoot AWS Bedrock access and IAM permission issues.

## Endpoints

### 1. Comprehensive Bedrock Access Check

**Endpoint:** `GET /bedrock/access-check`

**Purpose:** Performs a comprehensive check of Bedrock access including client connectivity, model availability, and actual model invocation tests.

**What it checks:**
- ✅ Bedrock client initialization
- ✅ Permission to list foundation models  
- ✅ Access to specific models (standard and premium)
- ✅ AWS identity information
- ✅ Model invocation capability

**Example Usage:**
```bash
curl http://localhost:8000/bedrock/access-check | jq .
```

**Response Format:**
```json
{
  "success": true,
  "message": "Bedrock access check completed",
  "timestamp": "2025-10-27T04:31:48.910346",
  "summary": {
    "accessible_models": 2,
    "total_models_tested": 4,
    "has_basic_access": true,
    "can_list_models": true
  },
  "detailed_results": {
    "bedrock_client": {...},
    "list_models": {...},
    "model_access": {...},
    "aws_identity": {...}
  },
  "recommendations": {...}
}
```

**Models Tested:**
- `anthropic.claude-3-haiku-20240307-v1:0` (Standard)
- `anthropic.claude-3-sonnet-20240229-v1:0` (Standard)
- `us.anthropic.claude-3-5-sonnet-20241022-v2:0` (Inference Profile)
- `us.anthropic.claude-sonnet-4-5-20250929-v1:0` (Premium Inference Profile)

### 2. IAM Permissions Check

**Endpoint:** `GET /bedrock/permissions`

**Purpose:** Specifically tests IAM permissions for Bedrock operations.

**What it checks:**
- ✅ `bedrock:ListFoundationModels` permission
- ✅ `bedrock:InvokeModel` permission
- ✅ `sts:GetCallerIdentity` permission

**Example Usage:**
```bash
curl http://localhost:8000/bedrock/permissions | jq .
```

**Response Format:**
```json
{
  "timestamp": "2025-10-27T04:32:01.705302",
  "permissions": {
    "bedrock:ListFoundationModels": {
      "status": "allowed",
      "details": "Can list 99 models"
    },
    "bedrock:InvokeModel": {
      "status": "allowed", 
      "details": "Successfully invoked model"
    },
    "sts:GetCallerIdentity": {
      "status": "allowed",
      "identity": {
        "account": "339712840004",
        "arn": "arn:aws:iam::339712840004:user/vasantharajan",
        "user_id": "AIDAU6GDWSFCMSDPV2HRU"
      }
    }
  },
  "overall_status": "good",
  "summary": {
    "allowed_permissions": 3,
    "total_permissions_checked": 3,
    "success_rate": "100.0%"
  }
}
```

## Current Status Analysis

Based on the test results:

### ✅ Working Properly
- **Basic Access**: Bedrock client connectivity ✅
- **IAM Permissions**: All core permissions granted ✅
- **Standard Models**: Claude 3 Haiku and Sonnet working ✅
- **Model Listing**: Can access 99 foundation models ✅
- **AWS Identity**: Properly authenticated ✅

### ⚠️ Requires Attention
- **Premium Models**: Claude 3.5 and 4.5 Sonnet blocked by payment instrument
- **Error**: "INVALID_PAYMENT_INSTRUMENT: A valid payment instrument must be provided"
- **Resolution**: Add payment method in AWS console for premium model access

## Error Analysis

### Payment Instrument Error
**Error Code:** `AccessDeniedException`
**Message:** "Model access is denied due to INVALID_PAYMENT_INSTRUMENT"

**Cause:** Premium inference profile models require a valid payment method
**Solution:** 
1. Go to AWS Console → Bedrock
2. Navigate to Model Access
3. Add a valid payment method
4. Wait 15 minutes for changes to propagate

### Model Access Patterns
- **Standard Models** (`anthropic.claude-*`): Work with basic IAM permissions
- **Inference Profiles** (`us.anthropic.*`): Require payment method for premium features

## Diagnostic Workflow

1. **Start with Permissions Check:**
   ```bash
   curl http://localhost:8000/bedrock/permissions
   ```

2. **Run Comprehensive Access Check:**
   ```bash
   curl http://localhost:8000/bedrock/access-check
   ```

3. **Analyze Results:**
   - Check `overall_status` in permissions
   - Review `summary.accessible_models` in access check
   - Look at specific error codes for failed models

4. **Follow Recommendations:**
   - For permission issues: Check IAM policies
   - For payment issues: Add payment method in AWS console
   - For regional issues: Verify model availability in your region

## Integration with Care Plan Endpoints

These diagnostic endpoints complement the care plan generation endpoints:

- **Before using care plans**: Run access check to verify model availability
- **When debugging failures**: Use these endpoints to identify root cause
- **For model selection**: See which models are accessible before choosing

## HTTP Status Codes

### Access Check Endpoint
- `200`: Overall access successful (at least one model working)
- `503`: No model access available
- `500`: Unexpected error during check

### Permissions Check Endpoint
- `200`: Permission check completed (regardless of results)
- `500`: Unexpected error during check

## Monitoring & Troubleshooting

### Common Issues & Solutions

1. **No Model Access**
   - Check IAM permissions
   - Verify AWS credentials
   - Request model access in Bedrock console

2. **Payment Required**
   - Add payment method in AWS console
   - Wait 15 minutes for activation
   - Retry access check

3. **Regional Availability**
   - Verify models available in us-east-1
   - Check if region supports specific models

4. **Rate Limiting**
   - Implement exponential backoff
   - Use standard models for high-volume testing

### Best Practices

1. **Regular Health Checks**: Run these endpoints periodically to monitor access
2. **Model Fallbacks**: Use access check results to implement model fallback logic
3. **Error Handling**: Parse error codes and recommendations for user-friendly messages
4. **Cost Management**: Monitor premium model usage to control costs

## Example Integration

```python
# Check access before generating care plan
access_result = requests.get("http://localhost:8000/bedrock/access-check").json()

if access_result["success"]:
    accessible_models = [
        model for model, result in access_result["detailed_results"]["model_access"].items()
        if result["status"] == "success"
    ]
    
    # Use the first accessible model
    if accessible_models:
        model_to_use = accessible_models[0]
        # Generate care plan with accessible model
    else:
        # Fall back to demo endpoint
        pass
else:
    # Handle no access scenario
    pass
```

This comprehensive diagnostic system ensures reliable Bedrock integration and helps quickly identify and resolve access issues.