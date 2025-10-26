"""
Care Plan Module

This module handles the generation of care plans from doctor prescriptions
using Amazon Bedrock AI services.
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import boto3
from botocore.exceptions import ClientError
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class PrescriptionItem(BaseModel):
    """Individual prescription item"""
    medication_name: str = Field(..., description="Name of the medication")
    dosage: str = Field(..., description="Dosage amount and frequency")
    duration: str = Field(..., description="Duration of treatment")
    instructions: Optional[str] = Field(None, description="Special instructions")


class PatientInfo(BaseModel):
    """Patient information"""
    age: int = Field(..., description="Patient age")
    gender: str = Field(..., description="Patient gender")
    weight: Optional[float] = Field(None, description="Patient weight in kg")
    medical_conditions: Optional[List[str]] = Field(default_factory=list, description="Existing medical conditions")
    allergies: Optional[List[str]] = Field(default_factory=list, description="Known allergies")


class DoctorPrescription(BaseModel):
    """Complete doctor prescription"""
    patient_info: PatientInfo
    diagnosis: str = Field(..., description="Medical diagnosis")
    prescriptions: List[PrescriptionItem] = Field(..., description="List of prescribed medications")
    doctor_notes: Optional[str] = Field(None, description="Additional doctor notes")
    prescription_date: Optional[str] = Field(default_factory=lambda: datetime.now().isoformat())


class CarePlanSection(BaseModel):
    """Individual section of a care plan"""
    title: str
    content: str
    priority: str = Field(default="medium", description="Priority level: high, medium, low")


class CarePlan(BaseModel):
    """Generated care plan response"""
    patient_summary: str
    care_goals: List[str]
    medication_management: List[CarePlanSection]
    lifestyle_recommendations: List[CarePlanSection]
    monitoring_schedule: List[CarePlanSection]
    warning_signs: List[str]
    follow_up_recommendations: List[CarePlanSection]
    generated_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class BedrockCarePlanGenerator:
    """
    Amazon Bedrock integration for generating care plans from prescriptions
    """
    
    def __init__(self, aws_access_key_id: Optional[str] = None,
                 aws_secret_access_key: Optional[str] = None,
                 aws_role_arn: Optional[str] = None,
                 region_name: str = "us-east-1"):
        """
        Initialize Bedrock client
        
        Args:
            aws_access_key_id: AWS access key ID
            aws_secret_access_key: AWS secret access key
            aws_role_arn: AWS role ARN for role-based access
            region_name: AWS region name
        """
        try:
            if aws_role_arn:
                # Use role-based access
                sts_client = boto3.client('sts',
                    aws_access_key_id=aws_access_key_id,
                    aws_secret_access_key=aws_secret_access_key,
                    region_name=region_name
                )
                
                assumed_role = sts_client.assume_role(
                    RoleArn=aws_role_arn,
                    RoleSessionName='BedrockCarePlanSession'
                )
                
                credentials = assumed_role['Credentials']
                self.bedrock_client = boto3.client(
                    'bedrock-runtime',
                    aws_access_key_id=credentials['AccessKeyId'],
                    aws_secret_access_key=credentials['SecretAccessKey'],
                    aws_session_token=credentials['SessionToken'],
                    region_name=region_name
                )
                logger.info(f"Using role-based access with role: {aws_role_arn}")
                
            elif aws_access_key_id and aws_secret_access_key:
                self.bedrock_client = boto3.client(
                    'bedrock-runtime',
                    aws_access_key_id=aws_access_key_id,
                    aws_secret_access_key=aws_secret_access_key,
                    region_name=region_name
                )
                logger.info("Using access key-based authentication")
            else:
                # Use default credentials
                self.bedrock_client = boto3.client('bedrock-runtime', region_name=region_name)
                logger.info("Using default AWS credentials")
                
        except Exception as e:
            logger.error(f"Failed to initialize Bedrock client: {e}")
            raise
    
    def _create_prompt(self, prescription: DoctorPrescription) -> str:
        """
        Create a structured prompt for Bedrock to generate care plan
        
        Args:
            prescription: Doctor prescription data
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""
You are an experienced healthcare AI assistant. Based on the following doctor's prescription and patient information, create a comprehensive care plan.

PATIENT INFORMATION:
- Age: {prescription.patient_info.age}
- Gender: {prescription.patient_info.gender}
- Weight: {prescription.patient_info.weight or 'Not specified'} kg
- Medical Conditions: {', '.join(prescription.patient_info.medical_conditions) if prescription.patient_info.medical_conditions else 'None specified'}
- Allergies: {', '.join(prescription.patient_info.allergies) if prescription.patient_info.allergies else 'None specified'}

DIAGNOSIS: {prescription.diagnosis}

PRESCRIBED MEDICATIONS:
"""
        
        for i, med in enumerate(prescription.prescriptions, 1):
            prompt += f"""
{i}. {med.medication_name}
   - Dosage: {med.dosage}
   - Duration: {med.duration}
   - Instructions: {med.instructions or 'Standard administration'}
"""
        
        if prescription.doctor_notes:
            prompt += f"\nDOCTOR'S NOTES: {prescription.doctor_notes}"
        
        prompt += """

Please provide a comprehensive care plan in JSON format with the following structure:
{
  "patient_summary": "Brief summary of patient condition and treatment approach",
  "care_goals": ["Goal 1", "Goal 2", "Goal 3"],
  "medication_management": [
    {
      "title": "Medication Schedule",
      "content": "Detailed medication timing and administration instructions",
      "priority": "high"
    }
  ],
  "lifestyle_recommendations": [
    {
      "title": "Diet and Nutrition",
      "content": "Specific dietary recommendations",
      "priority": "medium"
    }
  ],
  "monitoring_schedule": [
    {
      "title": "Vital Signs Monitoring",
      "content": "What to monitor and how often",
      "priority": "high"
    }
  ],
  "warning_signs": ["Warning sign 1", "Warning sign 2"],
  "follow_up_recommendations": [
    {
      "title": "Next Appointment",
      "content": "When and why to schedule follow-up",
      "priority": "high"
    }
  ]
}

Focus on:
1. Medication safety and interactions
2. Practical daily management
3. Monitoring for side effects
4. Lifestyle modifications specific to the condition
5. Clear timeline for recovery/management

Provide only the JSON response, no additional text.
"""
        return prompt
    
    async def generate_care_plan(self, prescription: DoctorPrescription, 
                                model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0") -> CarePlan:
        """
        Generate care plan using Amazon Bedrock
        
        Args:
            prescription: Doctor prescription data
            model_id: Bedrock model identifier
            
        Returns:
            Generated care plan
        """
        try:
            prompt = self._create_prompt(prescription)
            
            # Prepare request body based on model type
            if "anthropic.claude" in model_id:
                body = {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 4000,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.3,
                    "top_p": 0.9
                }
            elif "amazon.titan" in model_id:
                body = {
                    "inputText": prompt,
                    "textGenerationConfig": {
                        "maxTokenCount": 4000,
                        "temperature": 0.3,
                        "topP": 0.9
                    }
                }
            else:
                # Default to Claude format
                body = {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 4000,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.3
                }
            
            # Call Bedrock
            response = self.bedrock_client.invoke_model(
                modelId=model_id,
                body=json.dumps(body),
                contentType='application/json',
                accept='application/json'
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            
            # Extract content based on model type
            if "anthropic.claude" in model_id:
                content = response_body['content'][0]['text']
            elif "amazon.titan" in model_id:
                content = response_body['results'][0]['outputText']
            else:
                content = response_body.get('content', [{}])[0].get('text', '')
            
            # Parse JSON response
            try:
                care_plan_data = json.loads(content.strip())
                care_plan = CarePlan(**care_plan_data)
                
                logger.info(f"Successfully generated care plan for diagnosis: {prescription.diagnosis}")
                return care_plan
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse Bedrock response as JSON: {e}")
                # Fallback: create basic care plan
                return self._create_fallback_care_plan(prescription, content)
                
        except ClientError as e:
            error_code = e.response['Error']['Code']
            logger.error(f"Bedrock API error: {error_code} - {str(e)}")
            
            if error_code == 'AccessDeniedException':
                raise Exception("Access denied to Amazon Bedrock. Check IAM permissions.")
            elif error_code == 'ValidationException':
                raise Exception("Invalid request to Bedrock. Check model ID and parameters.")
            else:
                raise Exception(f"Bedrock error: {error_code}")
                
        except Exception as e:
            logger.error(f"Unexpected error generating care plan: {str(e)}")
            raise Exception(f"Failed to generate care plan: {str(e)}")
    
    def _create_fallback_care_plan(self, prescription: DoctorPrescription, raw_content: str) -> CarePlan:
        """
        Create a basic care plan if Bedrock response parsing fails
        
        Args:
            prescription: Original prescription data
            raw_content: Raw response from Bedrock
            
        Returns:
            Basic care plan
        """
        return CarePlan(
            patient_summary=f"Patient with {prescription.diagnosis} requiring medication management and monitoring.",
            care_goals=[
                "Manage symptoms effectively",
                "Monitor for medication side effects",
                "Improve overall health outcomes"
            ],
            medication_management=[
                CarePlanSection(
                    title="Prescribed Medications",
                    content=f"Follow prescribed regimen for {len(prescription.prescriptions)} medication(s). Take as directed by physician.",
                    priority="high"
                )
            ],
            lifestyle_recommendations=[
                CarePlanSection(
                    title="General Health",
                    content="Maintain healthy diet, regular exercise as tolerated, and adequate rest.",
                    priority="medium"
                )
            ],
            monitoring_schedule=[
                CarePlanSection(
                    title="Regular Check-ups",
                    content="Schedule follow-up appointments as recommended by healthcare provider.",
                    priority="high"
                )
            ],
            warning_signs=[
                "Worsening of symptoms",
                "Unusual side effects",
                "Signs of allergic reaction"
            ],
            follow_up_recommendations=[
                CarePlanSection(
                    title="Next Steps",
                    content="Contact healthcare provider if symptoms persist or worsen.",
                    priority="high"
                )
            ]
        )
    
    def list_available_models(self) -> List[str]:
        """
        List available Bedrock models for care plan generation
        
        Returns:
            List of available model IDs
        """
        try:
            bedrock_client = boto3.client('bedrock')
            response = bedrock_client.list_foundation_models()
            
            # Filter for text generation models suitable for care plans
            suitable_models = []
            for model in response.get('modelSummaries', []):
                if 'TEXT' in model.get('outputModalities', []):
                    suitable_models.append(model['modelId'])
            
            return suitable_models
            
        except Exception as e:
            logger.error(f"Failed to list Bedrock models: {e}")
            # Return common model IDs as fallback including latest Claude models
            return [
                "anthropic.claude-sonnet-4-5-20250929-v1:0",
                "anthropic.claude-3-5-sonnet-20241022-v2:0", 
                "anthropic.claude-3-sonnet-20240229-v1:0",
                "anthropic.claude-3-haiku-20240307-v1:0",
                "amazon.titan-text-express-v1"
            ]