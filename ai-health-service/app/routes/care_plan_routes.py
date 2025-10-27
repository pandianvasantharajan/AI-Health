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


@router.post("/generate")
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


@router.post("/sample")
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


@router.post("/claude-35-sonnet")
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


@router.post("/claude-35-sonnet/sample")
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


@router.post("/claude-3-sonnet")
async def generate_care_plan_claude_3(
    prescription: DoctorPrescription,
    care_plan_generator: BedrockCarePlanGenerator = Depends(get_care_plan_generator)
):
    """
    Generate a care plan using Claude 3 Sonnet (standard model).
    
    Args:
        prescription: Doctor prescription with patient info and medications
        care_plan_generator: Bedrock care plan generator dependency
    
    Returns:
        JSON response with generated care plan using Claude 3 Sonnet
    """
    try:
        # Generate care plan using Claude 3 Sonnet
        care_plan = await care_plan_generator.generate_care_plan(
            prescription=prescription,
            model_id=settings.claude_3_sonnet_model_id
        )
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Care plan generated successfully with Claude 3 Sonnet",
                "care_plan": care_plan.dict(),
                "model_used": settings.claude_3_sonnet_model_id,
                "diagnosis": prescription.diagnosis,
                "model_type": "Claude 3 Sonnet (Standard)"
            }
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error in generate_care_plan_claude_3 endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate care plan with Claude 3 Sonnet: {str(e)}"
        )


@router.post("/claude-3-sonnet/sample")
async def generate_sample_care_plan_claude_3(
    care_plan_generator: BedrockCarePlanGenerator = Depends(get_care_plan_generator)
):
    """
    Generate a care plan using sample prescription data with Claude 3 Sonnet.
    
    Args:
        care_plan_generator: Bedrock care plan generator dependency
    
    Returns:
        JSON response with generated care plan from sample data using Claude 3 Sonnet
    """
    try:
        # Sample prescription data for Claude 3 Sonnet
        sample_prescription = DoctorPrescription(
            patient_info=PatientInfo(
                age=55,
                gender="Male",
                weight=82.0,
                medical_conditions=["Type 2 Diabetes", "High cholesterol"],
                allergies=["Sulfa drugs"]
            ),
            diagnosis="Bacterial pneumonia with comorbidities",
            prescriptions=[
                PrescriptionItem(
                    medication_name="Ceftriaxone",
                    dosage="1g IV daily",
                    duration="7 days",
                    instructions="Administer over 30 minutes via IV infusion"
                ),
                PrescriptionItem(
                    medication_name="Prednisone",
                    dosage="40mg daily for 5 days, then taper",
                    duration="10 days total",
                    instructions="Take with food to reduce stomach irritation"
                ),
                PrescriptionItem(
                    medication_name="Albuterol nebulizer",
                    dosage="2.5mg every 6 hours",
                    duration="7 days",
                    instructions="Use as needed for breathing difficulty"
                )
            ],
            doctor_notes="Patient admitted for IV antibiotics. Monitor blood glucose closely due to steroid use. Continue home diabetes medications. Chest X-ray improvement expected by day 3-5."
        )
        
        # Generate care plan using Claude 3 Sonnet
        care_plan = await care_plan_generator.generate_care_plan(
            prescription=sample_prescription,
            model_id=settings.claude_3_sonnet_model_id
        )
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Sample care plan generated successfully with Claude 3 Sonnet",
                "care_plan": care_plan.dict(),
                "sample_prescription": sample_prescription.dict(),
                "model_used": settings.claude_3_sonnet_model_id,
                "model_type": "Claude 3 Sonnet (Standard)"
            }
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error in generate_sample_care_plan_claude_3 endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate sample care plan with Claude 3 Sonnet: {str(e)}"
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


@router.post("/compare")
async def compare_care_plans(
    prescription: DoctorPrescription,
    care_plan_generator: BedrockCarePlanGenerator = Depends(get_care_plan_generator)
):
    """
    Generate care plans using Claude 4.5, 3.5, 3.7, and 3 Sonnet for comparison.
    
    Args:
        prescription: Doctor prescription with patient info and medications
        care_plan_generator: Bedrock care plan generator dependency
    
    Returns:
        JSON response with care plans from all models for comparison
    """
    try:
        results = {}
        
        # Generate care plan with Claude 4.5 Sonnet (Premium)
        try:
            care_plan_45 = await care_plan_generator.generate_care_plan(
                prescription=prescription,
                model_id=settings.bedrock_model_id
            )
            results["claude_4_5_sonnet"] = {
                "success": True,
                "care_plan": care_plan_45.dict(),
                "model_used": settings.bedrock_model_id,
                "model_type": "Premium"
            }
        except Exception as e:
            results["claude_4_5_sonnet"] = {
                "success": False,
                "error": str(e),
                "model_used": settings.bedrock_model_id,
                "model_type": "Premium"
            }
        
        # Generate care plan with Claude 3.5 Sonnet (Standard)
        try:
            care_plan_35 = await care_plan_generator.generate_care_plan(
                prescription=prescription,
                model_id=settings.claude_35_sonnet_model_id
            )
            results["claude_3_5_sonnet"] = {
                "success": True,
                "care_plan": care_plan_35.dict(),
                "model_used": settings.claude_35_sonnet_model_id,
                "model_type": "Standard"
            }
        except Exception as e:
            results["claude_3_5_sonnet"] = {
                "success": False,
                "error": str(e),
                "model_used": settings.claude_35_sonnet_model_id,
                "model_type": "Standard"
            }
        
        # Generate care plan with Claude 3.7 Sonnet (Latest Standard)
        try:
            care_plan_37 = await care_plan_generator.generate_care_plan(
                prescription=prescription,
                model_id=settings.claude_37_sonnet_model_id
            )
            results["claude_3_7_sonnet"] = {
                "success": True,
                "care_plan": care_plan_37.dict(),
                "model_used": settings.claude_37_sonnet_model_id,
                "model_type": "Latest Standard"
            }
        except Exception as e:
            results["claude_3_7_sonnet"] = {
                "success": False,
                "error": str(e),
                "model_used": settings.claude_37_sonnet_model_id,
                "model_type": "Latest Standard"
            }
        
        # Generate care plan with Claude 3 Sonnet (Standard)
        try:
            care_plan_3 = await care_plan_generator.generate_care_plan(
                prescription=prescription,
                model_id=settings.claude_3_sonnet_model_id
            )
            results["claude_3_sonnet"] = {
                "success": True,
                "care_plan": care_plan_3.dict(),
                "model_used": settings.claude_3_sonnet_model_id,
                "model_type": "Standard"
            }
        except Exception as e:
            results["claude_3_sonnet"] = {
                "success": False,
                "error": str(e),
                "model_used": settings.claude_3_sonnet_model_id,
                "model_type": "Standard"
            }
        
        # Generate care plan with Amazon Nova Micro
        try:
            care_plan_nova = await care_plan_generator.generate_care_plan(
                prescription=prescription,
                model_id=settings.nova_micro_model_id
            )
            results["nova_micro"] = {
                "success": True,
                "care_plan": care_plan_nova.dict(),
                "model_used": settings.nova_micro_model_id,
                "model_type": "Amazon Nova"
            }
        except Exception as e:
            results["nova_micro"] = {
                "success": False,
                "error": str(e),
                "model_used": settings.nova_micro_model_id,
                "model_type": "Amazon Nova"
            }
        
        # Check if at least one model succeeded
        successful_models = sum(1 for result in results.values() if result.get("success", False))
        overall_success = successful_models > 0
        
        return JSONResponse(
            status_code=200 if overall_success else 500,
            content={
                "success": overall_success,
                "message": "Care plan comparison completed",
                "diagnosis": prescription.diagnosis,
                "successful_models": successful_models,
                "total_models": len(results),
                "results": results,
                "comparison_notes": {
                    "claude_4_5": "Premium model with enhanced capabilities (requires payment)",
                    "claude_3_7": "Latest standard model with improved capabilities",
                    "claude_3_5": "Standard model with proven performance",
                    "claude_3": "Baseline standard model, reliable and cost-effective",
                    "nova_micro": "Amazon Nova Micro - Fast, cost-effective text generation"
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Unexpected error in compare_care_plans endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to compare care plans: {str(e)}"
        )


@router.get("/models")
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
                "claude_3_7_sonnet": {
                    "model_id": settings.claude_37_sonnet_model_id,
                    "type": "Latest Standard",
                    "description": "Claude 3.7 Sonnet - Latest standard model with improved capabilities",
                    "endpoint": "/care-plan/claude-37-sonnet or /care-plan/claude-37-sonnet/sample"
                },
                "claude_3_5_sonnet": {
                    "model_id": settings.claude_35_sonnet_model_id,
                    "type": "Standard", 
                    "description": "Claude 3.5 Sonnet - Proven standard model",
                    "endpoint": "/care-plan/claude-35-sonnet or /care-plan/claude-35-sonnet/sample"
                },
                "claude_3_sonnet": {
                    "model_id": settings.claude_3_sonnet_model_id,
                    "type": "Standard",
                    "description": "Claude 3 Sonnet - Baseline standard model, reliable and cost-effective",
                    "endpoint": "/care-plan/claude-3-sonnet or /care-plan/claude-3-sonnet/sample"
                },
                "nova_micro": {
                    "model_id": settings.nova_micro_model_id,
                    "type": "Amazon Nova",
                    "description": "Amazon Nova Micro - Fast, cost-effective text generation model",
                    "endpoint": "/care-plan/nova-micro or /care-plan/nova-micro/sample"
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


@router.post("/demo")
async def generate_demo_care_plan():
    """
    Generate a demo care plan without calling Bedrock - shows expected structure.
    
    Returns:
        JSON response with demo care plan structure
    """
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
            "note": "This is a demo showing the expected care plan structure. Use other endpoints for AI-generated plans.",
            "care_plan": demo_care_plan.dict(),
            "sample_prescription": sample_prescription.dict(),
            "bedrock_required": False
        }
    )