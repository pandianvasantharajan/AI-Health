from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
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
            "current_default": settings.bedrock_model_id,
            "total_models": len(available_models)
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