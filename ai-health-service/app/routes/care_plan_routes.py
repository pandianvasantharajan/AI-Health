"""
Care Plan Generation Routes

This module contains all endpoints related to AI-powered care plan generation using Amazon Bedrock.
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
import logging
from typing import Optional
from datetime import datetime

from ..config import settings
from ..modules.care_plan import (
    BedrockCarePlanGenerator, 
    DoctorPrescription, 
    CarePlan, 
    PatientInfo, 
    PrescriptionItem,
    CarePlanSection
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/care-plan", tags=["Care Plan Generation"])


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






@router.post("/claude-37-sonnet")
async def generate_care_plan_claude_37(
    prescription: DoctorPrescription,
    care_plan_generator: BedrockCarePlanGenerator = Depends(get_care_plan_generator)
):
    """
    Generate a care plan using Claude 3.7 Sonnet (latest standard model).
    
    Args:
        prescription: Doctor prescription with patient info and medications
        care_plan_generator: Bedrock care plan generator dependency
    
    Returns:
        JSON response with generated care plan using Claude 3.7 Sonnet
    """
    try:
        # Generate care plan using Claude 3.7 Sonnet
        care_plan = await care_plan_generator.generate_care_plan(
            prescription=prescription,
            model_id=settings.claude_37_sonnet_model_id
        )
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Care plan generated successfully with Claude 3.7 Sonnet",
                "care_plan": care_plan.dict(),
                "model_used": settings.claude_37_sonnet_model_id,
                "diagnosis": prescription.diagnosis,
                "model_type": "Claude 3.7 Sonnet (Latest Standard)"
            }
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error in generate_care_plan_claude_37 endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate care plan with Claude 3.7 Sonnet: {str(e)}"
        )


@router.post("/claude-37-sonnet/sample")
async def generate_sample_care_plan_claude_37(
    care_plan_generator: BedrockCarePlanGenerator = Depends(get_care_plan_generator)
):
    """
    Generate a care plan using sample prescription data with Claude 3.7 Sonnet.
    
    Args:
        care_plan_generator: Bedrock care plan generator dependency
    
    Returns:
        JSON response with generated care plan from sample data using Claude 3.7 Sonnet
    """
    try:
        # Sample prescription data
        sample_prescription = DoctorPrescription(
            patient_info=PatientInfo(
                age=32,
                gender="Male",
                weight=75.0,
                medical_conditions=["Mild asthma"],
                allergies=["Shellfish"]
            ),
            diagnosis="Upper respiratory tract infection",
            prescriptions=[
                PrescriptionItem(
                    medication_name="Azithromycin",
                    dosage="500mg on day 1, then 250mg daily",
                    duration="5 days",
                    instructions="Take on empty stomach 1 hour before or 2 hours after meals"
                ),
                PrescriptionItem(
                    medication_name="Guaifenesin",
                    dosage="400mg every 4 hours",
                    duration="7 days",
                    instructions="Take with plenty of water to help loosen mucus"
                ),
                PrescriptionItem(
                    medication_name="Throat lozenges",
                    dosage="As needed",
                    duration="Until symptoms resolve",
                    instructions="Use for throat discomfort, maximum 6 per day"
                )
            ],
            doctor_notes="Patient has mild asthma but well-controlled. Watch for any respiratory distress. Continue usual asthma medications. Return if symptoms worsen or persist beyond 7 days."
        )
        
        # Generate care plan using Claude 3.7 Sonnet
        care_plan = await care_plan_generator.generate_care_plan(
            prescription=sample_prescription,
            model_id=settings.claude_37_sonnet_model_id
        )
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Sample care plan generated successfully with Claude 3.7 Sonnet",
                "care_plan": care_plan.dict(),
                "sample_prescription": sample_prescription.dict(),
                "model_used": settings.claude_37_sonnet_model_id,
                "model_type": "Claude 3.7 Sonnet (Latest Standard)"
            }
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error in generate_sample_care_plan_claude_37 endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate sample care plan with Claude 3.7 Sonnet: {str(e)}"
        )





# ================================ AMAZON NOVA MICRO ENDPOINTS ================================

@router.post("/nova-micro")
async def generate_care_plan_nova_micro(
    prescription: DoctorPrescription,
    care_plan_generator: BedrockCarePlanGenerator = Depends(get_care_plan_generator)
):
    """
    Generate comprehensive care plan using Amazon Nova Micro.
    
    This endpoint generates medical care plans based on doctor prescriptions using
    Amazon Nova Micro - a fast, cost-effective text generation model.
    
    Args:
        prescription: Complete prescription data including patient info, diagnosis, medications, and doctor notes
        care_plan_generator: Bedrock care plan generator dependency
    
    Returns:
        JSON response with generated care plan and metadata
    """
    try:
        logger.info(f"🏥 Generating care plan with Nova Micro for: {prescription.diagnosis}")
        
        # Generate care plan using Amazon Nova Micro
        care_plan = await care_plan_generator.generate_care_plan(
            prescription=prescription,
            model_id=settings.nova_micro_model_id
        )
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Care plan generated successfully with Amazon Nova Micro",
                "care_plan": care_plan.dict(),
                "diagnosis": prescription.diagnosis,
                "model_used": settings.nova_micro_model_id,
                "model_type": "Amazon Nova Micro"
            }
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error generating care plan with Nova Micro: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate care plan with Amazon Nova Micro: {str(e)}"
        )


@router.post("/nova-micro/sample")
async def generate_sample_care_plan_nova_micro(
    care_plan_generator: BedrockCarePlanGenerator = Depends(get_care_plan_generator)
):
    """
    Generate a sample care plan using Amazon Nova Micro with predefined patient data.
    
    This endpoint demonstrates care plan generation capabilities using Amazon Nova Micro
    with a complex patient case involving multiple conditions and medications.
    
    Args:
        care_plan_generator: Bedrock care plan generator dependency
    
    Returns:
        JSON response with generated care plan using sample prescription data
    """
    try:
        logger.info("🧪 Generating sample care plan with Amazon Nova Micro")
        
        # Create comprehensive sample prescription for medical factors demonstration
        sample_prescription = DoctorPrescription(
            patient_info=PatientInfo(
                age=65,
                gender="Female", 
                weight=68.0,
                medical_conditions=["Hypertension", "Type 2 Diabetes", "Chronic Kidney Disease Stage 3"],
                allergies=["Penicillin", "Iodine contrast"]
            ),
            diagnosis="Acute exacerbation of chronic heart failure with reduced ejection fraction",
            prescriptions=[
                PrescriptionItem(
                    medication_name="Furosemide",
                    dosage="40mg twice daily",
                    duration="14 days, then reassess",
                    instructions="Take with food. Monitor weight daily. Report weight gain >2lbs in 24hrs"
                ),
                PrescriptionItem(
                    medication_name="Metoprolol succinate",
                    dosage="25mg daily",
                    duration="Ongoing",
                    instructions="Take with or without food. Do not stop abruptly. Check pulse before taking"
                ),
                PrescriptionItem(
                    medication_name="Lisinopril",
                    dosage="5mg daily",
                    duration="Ongoing",
                    instructions="Take at same time daily. Avoid potassium supplements. Monitor kidney function"
                ),
                PrescriptionItem(
                    medication_name="Metformin",
                    dosage="500mg twice daily",
                    duration="Ongoing",
                    instructions="Take with meals. Hold if contrast study or surgery planned"
                )
            ],
            doctor_notes="Patient presents with dyspnea, peripheral edema, and weight gain. Chest X-ray shows pulmonary edema. BNP elevated at 850. Creatinine 1.8 (baseline 1.5). Careful fluid balance management needed. Follow up in 1 week for weight and symptoms. Cardiology referral if no improvement."
        )
        
        # Generate care plan using Amazon Nova Micro
        care_plan = await care_plan_generator.generate_care_plan(
            prescription=sample_prescription,
            model_id=settings.nova_micro_model_id
        )
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Sample care plan generated successfully with Amazon Nova Micro",
                "care_plan": care_plan.dict(),
                "sample_prescription": sample_prescription.dict(),
                "model_used": settings.nova_micro_model_id,
                "model_type": "Amazon Nova Micro",
                "medical_factors_focus": {
                    "primary_conditions": ["Heart Failure", "Diabetes", "Hypertension", "CKD"],
                    "key_considerations": ["Fluid management", "Kidney function monitoring", "Drug interactions"],
                    "complexity_level": "High - multiple comorbidities requiring careful coordination"
                }
            }
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error in generate_sample_care_plan_nova_micro endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate sample care plan with Amazon Nova Micro: {str(e)}"
        )


