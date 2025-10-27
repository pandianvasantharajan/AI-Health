"""
Bedrock Access and Permission Check Routes

This module contains endpoints for diagnosing AWS Bedrock access and IAM permissions.
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
import logging
import json
import boto3
from datetime import datetime
from botocore.exceptions import ClientError
from typing import Dict, Any

from ..config import settings
from ..modules.care_plan import BedrockCarePlanGenerator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/bedrock", tags=["Bedrock Access"])


def get_care_plan_generator() -> BedrockCarePlanGenerator:
    """
    Dependency to get Bedrock care plan generator instance.
    """
    return BedrockCarePlanGenerator(
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
        region_name=settings.effective_bedrock_region,
        aws_role_arn=settings.aws_role_arn
    )


@router.get("/access-check")
async def check_bedrock_access(
    care_plan_generator: BedrockCarePlanGenerator = Depends(get_care_plan_generator)
):
    """
    Check AWS Bedrock access and IAM permissions.
    
    This endpoint performs comprehensive checks to verify:
    - Bedrock client connectivity
    - IAM permissions to list models
    - Access to specific models (standard and premium)
    - AWS identity information
    
    Returns:
        JSON response with detailed access check results
    """
    try:
        access_results = care_plan_generator.check_bedrock_access()
        
        # Determine HTTP status based on overall access
        status_code = 200 if access_results.get("overall_access", False) else 503
        
        return JSONResponse(
            status_code=status_code,
            content={
                "success": access_results.get("overall_access", False),
                "message": "Bedrock access check completed",
                "timestamp": access_results.get("timestamp"),
                "summary": access_results.get("summary", {}),
                "detailed_results": access_results.get("checks", {}),
                "recommendations": {
                    "if_no_access": [
                        "Verify AWS credentials are valid",
                        "Check IAM permissions for Bedrock access",
                        "Ensure models are available in your region",
                        "Request access to models in AWS Bedrock console"
                    ],
                    "for_premium_models": [
                        "Add payment method for Claude 4.5 Sonnet",
                        "Use inference profile IDs (us.anthropic.* format)",
                        "Check billing configuration in AWS console"
                    ]
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Unexpected error in bedrock access check endpoint: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Failed to perform Bedrock access check",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )


@router.get("/permissions")
async def check_bedrock_permissions():
    """
    Check specific IAM permissions for Bedrock access.
    
    Returns:
        JSON response with IAM permission analysis
    """
    try:
        permissions_check = {
            "timestamp": datetime.now().isoformat(),
            "permissions": {},
            "overall_status": "unknown"
        }
        
        # Test different Bedrock permissions
        region = settings.effective_bedrock_region
        
        # Check bedrock:ListFoundationModels
        try:
            bedrock_client = boto3.client('bedrock', region_name=region)
            response = bedrock_client.list_foundation_models()
            permissions_check["permissions"]["bedrock:ListFoundationModels"] = {
                "status": "allowed",
                "details": f"Can list {len(response.get('modelSummaries', []))} models"
            }
        except ClientError as e:
            permissions_check["permissions"]["bedrock:ListFoundationModels"] = {
                "status": "denied",
                "error_code": e.response['Error']['Code'],
                "message": e.response['Error']['Message']
            }
        except Exception as e:
            permissions_check["permissions"]["bedrock:ListFoundationModels"] = {
                "status": "error",
                "message": str(e)
            }
        
        # Check bedrock:InvokeModel
        try:
            bedrock_runtime = boto3.client('bedrock-runtime', region_name=region)
            # Try a minimal invoke to test permission (will likely fail on model access, but tests permission)
            test_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1,
                "messages": [{"role": "user", "content": "Hi"}]
            }
            
            # This will likely fail due to model access, but we can check the error type
            try:
                bedrock_runtime.invoke_model(
                    modelId="anthropic.claude-3-haiku-20240307-v1:0",
                    body=json.dumps(test_body),
                    contentType='application/json',
                    accept='application/json'
                )
                permissions_check["permissions"]["bedrock:InvokeModel"] = {
                    "status": "allowed",
                    "details": "Successfully invoked model"
                }
            except ClientError as invoke_error:
                error_code = invoke_error.response['Error']['Code']
                if error_code == 'AccessDeniedException':
                    if 'does not have access to model' in invoke_error.response['Error']['Message']:
                        permissions_check["permissions"]["bedrock:InvokeModel"] = {
                            "status": "permission_allowed_model_access_needed",
                            "details": "Has invoke permission but needs model access"
                        }
                    else:
                        permissions_check["permissions"]["bedrock:InvokeModel"] = {
                            "status": "denied",
                            "error_code": error_code,
                            "message": invoke_error.response['Error']['Message']
                        }
                else:
                    permissions_check["permissions"]["bedrock:InvokeModel"] = {
                        "status": "allowed_with_restrictions",
                        "details": f"Has permission but encountered: {error_code}"
                    }
                    
        except Exception as e:
            permissions_check["permissions"]["bedrock:InvokeModel"] = {
                "status": "error",
                "message": str(e)
            }
        
        # Check STS permissions (to get identity)
        try:
            sts_client = boto3.client('sts', region_name=region)
            identity = sts_client.get_caller_identity()
            permissions_check["permissions"]["sts:GetCallerIdentity"] = {
                "status": "allowed",
                "identity": {
                    "account": identity.get('Account'),
                    "arn": identity.get('Arn'),
                    "user_id": identity.get('UserId')
                }
            }
        except Exception as e:
            permissions_check["permissions"]["sts:GetCallerIdentity"] = {
                "status": "error",
                "message": str(e)
            }
        
        # Determine overall status
        allowed_permissions = sum(1 for perm in permissions_check["permissions"].values() 
                                 if perm["status"] in ["allowed", "permission_allowed_model_access_needed", "allowed_with_restrictions"])
        total_permissions = len(permissions_check["permissions"])
        
        if allowed_permissions == total_permissions:
            permissions_check["overall_status"] = "good"
        elif allowed_permissions > 0:
            permissions_check["overall_status"] = "partial"
        else:
            permissions_check["overall_status"] = "insufficient"
        
        permissions_check["summary"] = {
            "allowed_permissions": allowed_permissions,
            "total_permissions_checked": total_permissions,
            "success_rate": f"{(allowed_permissions/total_permissions*100):.1f}%" if total_permissions > 0 else "0%"
        }
        
        return JSONResponse(
            status_code=200,
            content=permissions_check
        )
        
    except Exception as e:
        logger.error(f"Unexpected error in bedrock permissions check: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Failed to check Bedrock permissions",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )