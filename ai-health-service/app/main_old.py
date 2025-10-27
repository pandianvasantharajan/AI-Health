from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import json
from datetime import datetime
from typing import Optional

from .config import settings
from .modules.file_upload import S3FileUploader
from .modules.care_plan import (
    BedrockCarePlanGenerator, 
    DoctorPrescription, 
    CarePlan, 
    PatientInfo, 
    PrescriptionItem
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI instance
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI Health Service - File Upload API"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_care_plan_generator() -> BedrockCarePlanGenerator:
    """
    Dependency to get Bedrock care plan generator instance.
    """
    return BedrockCarePlanGenerator(
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
        aws_role_arn=settings.aws_role_arn,
        region_name=settings.effective_bedrock_region
    )


def get_s3_uploader() -> S3FileUploader:
    """
    Dependency to get S3 uploader instance.
    """
    return S3FileUploader(
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
        region_name=settings.aws_region
    )


@app.get("/")
async def root():
    """
    Root endpoint.
    """
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "status": "healthy"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version
    }


@app.post("/upload/pdf")
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


@app.post("/upload/file")
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


@app.get("/file/{bucket_name}/{file_key:path}")
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


@app.post("/care-plan/generate")
async def generate_care_plan(
    prescription: DoctorPrescription,
    model_id: Optional[str] = None,
    care_plan_generator: BedrockCarePlanGenerator = Depends(get_care_plan_generator)
):
    """
    Generate a care plan from a doctor's prescription using Amazon Bedrock.
    
    Args:
        prescription: Doctor prescription with patient info and medications
        model_id: Optional Bedrock model ID (uses default if not specified)
        care_plan_generator: Bedrock care plan generator dependency
    
    Returns:
        JSON response with generated care plan
    """
    try:
        # Use default model if not specified
        effective_model_id = model_id or settings.bedrock_model_id
        
        # Generate care plan
        care_plan = await care_plan_generator.generate_care_plan(
            prescription=prescription,
            model_id=effective_model_id
        )
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Care plan generated successfully",
                "care_plan": care_plan.dict(),
                "model_used": effective_model_id,
                "diagnosis": prescription.diagnosis
            }
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error in generate_care_plan endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate care plan: {str(e)}"
        )


@app.post("/care-plan/sample")
async def generate_sample_care_plan(
    care_plan_generator: BedrockCarePlanGenerator = Depends(get_care_plan_generator)
):
    """
    Generate a care plan using sample prescription data for testing.
    
    Args:
        care_plan_generator: Bedrock care plan generator dependency
    
    Returns:
        JSON response with generated care plan from sample data
    """
    try:
        # Sample prescription data
        sample_prescription = DoctorPrescription(
            patient_info=PatientInfo(
                age=45,
                gender="Female",
                weight=68.5,
                medical_conditions=["Hypertension", "Type 2 Diabetes"],
                allergies=["Penicillin"]
            ),
            diagnosis="Acute bronchitis with underlying comorbidities",
            prescriptions=[
                PrescriptionItem(
                    medication_name="Amoxicillin-Clavulanate",
                    dosage="875mg/125mg twice daily",
                    duration="7 days",
                    instructions="Take with food to reduce stomach upset"
                ),
                PrescriptionItem(
                    medication_name="Dextromethorphan",
                    dosage="15mg every 4 hours as needed",
                    duration="Up to 7 days",
                    instructions="For cough suppression, do not exceed 6 doses per day"
                ),
                PrescriptionItem(
                    medication_name="Albuterol inhaler",
                    dosage="2 puffs every 4-6 hours as needed",
                    duration="30 days",
                    instructions="For shortness of breath or wheezing"
                )
            ],
            doctor_notes="Patient has well-controlled diabetes and hypertension. Monitor blood sugar levels during antibiotic treatment. Follow up if symptoms worsen or persist beyond 7 days."
        )
        
        # Generate care plan
        care_plan = await care_plan_generator.generate_care_plan(
            prescription=sample_prescription,
            model_id=settings.bedrock_model_id
        )
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Sample care plan generated successfully",
                "care_plan": care_plan.dict(),
                "sample_prescription": sample_prescription.dict(),
                "model_used": settings.bedrock_model_id
            }
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error in generate_sample_care_plan endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate sample care plan: {str(e)}"
        )


@app.post("/care-plan/claude-35-sonnet")
async def generate_care_plan_claude_35(
    prescription: DoctorPrescription,
    care_plan_generator: BedrockCarePlanGenerator = Depends(get_care_plan_generator)
):
    """
    Generate a care plan using Claude 3.5 Sonnet (standard model).
    
    Args:
        prescription: Doctor prescription with patient info and medications
        care_plan_generator: Bedrock care plan generator dependency
    
    Returns:
        JSON response with generated care plan using Claude 3.5 Sonnet
    """
    try:
        # Generate care plan using Claude 3.5 Sonnet
        care_plan = await care_plan_generator.generate_care_plan(
            prescription=prescription,
            model_id=settings.claude_35_sonnet_model_id
        )
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Care plan generated successfully with Claude 3.5 Sonnet",
                "care_plan": care_plan.dict(),
                "model_used": settings.claude_35_sonnet_model_id,
                "diagnosis": prescription.diagnosis,
                "model_type": "Claude 3.5 Sonnet (Standard)"
            }
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error in generate_care_plan_claude_35 endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate care plan with Claude 3.5 Sonnet: {str(e)}"
        )


@app.post("/care-plan/claude-35-sonnet/sample")
async def generate_sample_care_plan_claude_35(
    care_plan_generator: BedrockCarePlanGenerator = Depends(get_care_plan_generator)
):
    """
    Generate a care plan using sample prescription data with Claude 3.5 Sonnet.
    
    Args:
        care_plan_generator: Bedrock care plan generator dependency
    
    Returns:
        JSON response with generated care plan from sample data using Claude 3.5 Sonnet
    """
    try:
        # Sample prescription data
        sample_prescription = DoctorPrescription(
            patient_info=PatientInfo(
                age=45,
                gender="Female",
                weight=68.5,
                medical_conditions=["Hypertension", "Type 2 Diabetes"],
                allergies=["Penicillin"]
            ),
            diagnosis="Acute bronchitis with underlying comorbidities",
            prescriptions=[
                PrescriptionItem(
                    medication_name="Amoxicillin-Clavulanate",
                    dosage="875mg/125mg twice daily",
                    duration="7 days",
                    instructions="Take with food to reduce stomach upset"
                ),
                PrescriptionItem(
                    medication_name="Dextromethorphan",
                    dosage="15mg every 4 hours as needed",
                    duration="Up to 7 days",
                    instructions="For cough suppression, do not exceed 6 doses per day"
                ),
                PrescriptionItem(
                    medication_name="Albuterol inhaler",
                    dosage="2 puffs every 4-6 hours as needed",
                    duration="30 days",
                    instructions="For shortness of breath or wheezing"
                )
            ],
            doctor_notes="Patient has well-controlled diabetes and hypertension. Monitor blood sugar levels during antibiotic treatment. Follow up if symptoms worsen or persist beyond 7 days."
        )
        
        # Generate care plan using Claude 3.5 Sonnet
        care_plan = await care_plan_generator.generate_care_plan(
            prescription=sample_prescription,
            model_id=settings.claude_35_sonnet_model_id
        )
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Sample care plan generated successfully with Claude 3.5 Sonnet",
                "care_plan": care_plan.dict(),
                "sample_prescription": sample_prescription.dict(),
                "model_used": settings.claude_35_sonnet_model_id,
                "model_type": "Claude 3.5 Sonnet (Standard)"
            }
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error in generate_sample_care_plan_claude_35 endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate sample care plan with Claude 3.5 Sonnet: {str(e)}"
        )


@app.post("/care-plan/compare")
async def compare_care_plans(
    prescription: DoctorPrescription,
    care_plan_generator: BedrockCarePlanGenerator = Depends(get_care_plan_generator)
):
    """
    Generate care plans using both Claude 4.5 and Claude 3.5 Sonnet for comparison.
    
    Args:
        prescription: Doctor prescription with patient info and medications
        care_plan_generator: Bedrock care plan generator dependency
    
    Returns:
        JSON response with care plans from both models for comparison
    """
    try:
        # Generate care plan with Claude 4.5 Sonnet (Premium)
        try:
            care_plan_45 = await care_plan_generator.generate_care_plan(
                prescription=prescription,
                model_id=settings.bedrock_model_id
            )
            claude_45_result = {
                "success": True,
                "care_plan": care_plan_45.dict(),
                "model_used": settings.bedrock_model_id
            }
        except Exception as e:
            claude_45_result = {
                "success": False,
                "error": str(e),
                "model_used": settings.bedrock_model_id
            }
        
        # Generate care plan with Claude 3.5 Sonnet (Standard)
        try:
            care_plan_35 = await care_plan_generator.generate_care_plan(
                prescription=prescription,
                model_id=settings.claude_35_sonnet_model_id
            )
            claude_35_result = {
                "success": True,
                "care_plan": care_plan_35.dict(),
                "model_used": settings.claude_35_sonnet_model_id
            }
        except Exception as e:
            claude_35_result = {
                "success": False,
                "error": str(e),
                "model_used": settings.claude_35_sonnet_model_id
            }
        
        # Check if at least one model succeeded
        overall_success = claude_45_result.get("success", False) or claude_35_result.get("success", False)
        
        return JSONResponse(
            status_code=200 if overall_success else 500,
            content={
                "success": overall_success,
                "message": "Care plan comparison completed",
                "diagnosis": prescription.diagnosis,
                "claude_4_5_sonnet": claude_45_result,
                "claude_3_5_sonnet": claude_35_result,
                "comparison_notes": {
                    "claude_4_5": "Premium model with enhanced capabilities",
                    "claude_3_5": "Standard model with proven performance"
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Unexpected error in compare_care_plans endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to compare care plans: {str(e)}"
        )


@app.get("/bedrock/access-check")
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


@app.get("/bedrock/permissions")
async def check_bedrock_permissions():
    """
    Check specific IAM permissions for Bedrock access.
    
    Returns:
        JSON response with IAM permission analysis
    """
    try:
        import boto3
        from botocore.exceptions import ClientError
        
        permissions_check = {
            "timestamp": datetime.now().isoformat(),
            "permissions": {},
            "overall_status": "unknown"
        }
        
        # Test different Bedrock permissions
        region = "us-east-1"  # Use the configured region
        
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


@app.get("/care-plan/models")
async def list_bedrock_models(
    care_plan_generator: BedrockCarePlanGenerator = Depends(get_care_plan_generator)
):
    """
    List available Amazon Bedrock models for care plan generation.
    
    Args:
        care_plan_generator: Bedrock care plan generator dependency
    
    Returns:
        JSON response with list of available models
    """
    try:
        available_models = care_plan_generator.list_available_models()
        
        return {
            "success": True,
            "available_models": available_models,
            "configured_models": {
                "claude_4_5_sonnet": {
                    "model_id": settings.bedrock_model_id,
                    "type": "Premium",
                    "description": "Claude 4.5 Sonnet - Latest premium model with enhanced capabilities",
                    "endpoint": "/care-plan/generate (default) or /care-plan/sample"
                },
                "claude_3_5_sonnet": {
                    "model_id": settings.claude_35_sonnet_model_id,
                    "type": "Standard", 
                    "description": "Claude 3.5 Sonnet - Proven standard model",
                    "endpoint": "/care-plan/claude-35-sonnet or /care-plan/claude-35-sonnet/sample"
                }
            },
            "current_default": settings.bedrock_model_id,
            "total_models": len(available_models),
            "comparison_endpoint": "/care-plan/compare"
        }
        
    except Exception as e:
        logger.error(f"Unexpected error in list_bedrock_models endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list Bedrock models: {str(e)}"
        )


@app.post("/care-plan/demo")
async def generate_demo_care_plan():
    """
    Generate a demo care plan without calling Bedrock - shows expected structure.
    
    Returns:
        JSON response with demo care plan structure
    """
    from .modules.care_plan import CarePlan, CarePlanSection, PatientInfo, PrescriptionItem, DoctorPrescription
    
    # Sample prescription data
    sample_prescription = DoctorPrescription(
        patient_info=PatientInfo(
            age=45,
            gender="Female",
            weight=68.5,
            medical_conditions=["Hypertension", "Type 2 Diabetes"],
            allergies=["Penicillin"]
        ),
        diagnosis="Acute bronchitis with underlying comorbidities",
        prescriptions=[
            PrescriptionItem(
                medication_name="Amoxicillin-Clavulanate",
                dosage="875mg/125mg twice daily",
                duration="7 days",
                instructions="Take with food to reduce stomach upset"
            ),
            PrescriptionItem(
                medication_name="Dextromethorphan",
                dosage="15mg every 4 hours as needed",
                duration="Up to 7 days",
                instructions="For cough suppression, do not exceed 6 doses per day"
            )
        ],
        doctor_notes="Patient has well-controlled diabetes and hypertension. Monitor blood sugar levels during antibiotic treatment."
    )
    
    # Demo care plan (what Bedrock would generate)
    demo_care_plan = CarePlan(
        patient_summary="45-year-old female with acute bronchitis, complicated by well-controlled hypertension and type 2 diabetes. Requires antibiotic treatment with careful monitoring of blood glucose levels.",
        care_goals=[
            "Resolve acute bronchitis symptoms within 7-10 days",
            "Maintain stable blood glucose levels during antibiotic treatment",
            "Prevent complications and ensure medication adherence",
            "Monitor for signs of treatment response and potential side effects"
        ],
        medication_management=[
            CarePlanSection(
                title="Antibiotic Management",
                content="Take Amoxicillin-Clavulanate 875mg/125mg twice daily for 7 days. Take with food to minimize gastrointestinal upset. Complete the full course even if symptoms improve.",
                priority="high"
            ),
            CarePlanSection(
                title="Cough Management",
                content="Use Dextromethorphan 15mg every 4 hours as needed for cough. Do not exceed 6 doses per day. Discontinue if cough resolves.",
                priority="medium"
            ),
            CarePlanSection(
                title="Blood Sugar Monitoring",
                content="Monitor blood glucose levels more frequently during antibiotic treatment. Check 2-3 times daily and maintain diabetes medication regimen.",
                priority="high"
            )
        ],
        lifestyle_recommendations=[
            CarePlanSection(
                title="Rest and Recovery",
                content="Ensure adequate rest, aim for 7-8 hours of sleep nightly. Avoid strenuous activities until symptoms resolve.",
                priority="high"
            ),
            CarePlanSection(
                title="Hydration",
                content="Increase fluid intake to 8-10 glasses of water daily to help thin mucus and support recovery.",
                priority="medium"
            ),
            CarePlanSection(
                title="Nutrition",
                content="Maintain diabetic diet plan. Eat with medications to reduce stomach upset. Include probiotic foods to support gut health during antibiotic use.",
                priority="medium"
            )
        ],
        monitoring_schedule=[
            CarePlanSection(
                title="Daily Monitoring",
                content="Check blood glucose 2-3 times daily. Monitor temperature twice daily. Track cough severity and sputum production.",
                priority="high"
            ),
            CarePlanSection(
                title="Weekly Assessment",
                content="Evaluate overall symptom improvement. Assess medication tolerance and side effects.",
                priority="medium"
            )
        ],
        warning_signs=[
            "Worsening shortness of breath or chest pain",
            "Blood glucose levels consistently above 300 mg/dL",
            "Signs of severe allergic reaction (rash, difficulty breathing)",
            "Persistent fever above 101°F after 48 hours of treatment",
            "Severe diarrhea or signs of C. difficile infection",
            "No improvement in cough or symptoms after 5 days"
        ],
        follow_up_recommendations=[
            CarePlanSection(
                title="Primary Care Follow-up",
                content="Schedule follow-up appointment in 1-2 weeks if symptoms persist or worsen. Earlier if warning signs develop.",
                priority="high"
            ),
            CarePlanSection(
                title="Diabetes Management",
                content="Continue regular endocrinology appointments. Inform diabetes care team of antibiotic treatment.",
                priority="medium"
            )
        ]
    )
    
    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "message": "Demo care plan generated (structure example)",
            "note": "This is a demo showing the expected care plan structure. Use /care-plan/sample for Bedrock-generated plans.",
            "care_plan": demo_care_plan.dict(),
            "sample_prescription": sample_prescription.dict(),
            "bedrock_required": False
        }
    )


@app.get("/file/{bucket_name}/{file_key:path}")
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )