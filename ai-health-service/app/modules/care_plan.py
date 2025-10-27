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
        # ADD COMPREHENSIVE DEBUG LOGGING
        logger.info("=== BEDROCK CARE PLAN GENERATION DEBUG ===")
        logger.info(f"🎯 Model ID: {model_id}")
        logger.info(f"🏥 Diagnosis: {prescription.diagnosis}")
        logger.info(f"👤 Patient Age: {prescription.patient_info.age}")
        logger.info(f"🔑 AWS Region: {self.bedrock_client._client_config.region_name}")
        
        try:
            prompt = self._create_prompt(prescription)
            logger.info(f"📝 Prompt length: {len(prompt)} characters")
            
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
                logger.info("🤖 Using Claude format")
            elif "amazon.titan" in model_id:
                body = {
                    "inputText": prompt,
                    "textGenerationConfig": {
                        "maxTokenCount": 4000,
                        "temperature": 0.3,
                        "topP": 0.9
                    }
                }
                logger.info("🤖 Using Titan format")
            elif "amazon.nova" in model_id:
                body = {
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "text": prompt
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
                logger.info("🤖 Using Nova format")
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
                logger.info("🤖 Using default Claude format")
            
            logger.info(f"📦 Request body keys: {list(body.keys())}")
            logger.info(f"📏 Request body size: {len(json.dumps(body))} bytes")
            
            # Call Bedrock
            logger.info("🚀 Calling Bedrock API...")
            response = self.bedrock_client.invoke_model(
                modelId=model_id,
                body=json.dumps(body),
                contentType='application/json',
                accept='application/json'
            )
            
            logger.info("✅ Bedrock API call successful!")
            logger.info(f"📊 Response metadata: {response.get('ResponseMetadata', {})}")
            
            # Parse response
            response_body = json.loads(response['body'].read())
            logger.info(f"📋 Response body keys: {list(response_body.keys())}")
            
            # Extract content based on model type
            if "anthropic.claude" in model_id:
                content = response_body['content'][0]['text']
            elif "amazon.titan" in model_id:
                content = response_body['results'][0]['outputText']
            elif "amazon.nova" in model_id:
                content = response_body['output']['message']['content'][0]['text']
            else:
                content = response_body.get('content', [{}])[0].get('text', '')
            
            logger.info(f"📝 Generated content length: {len(content)} characters")
            
            # Parse JSON response
            try:
                care_plan_data = json.loads(content.strip())
                care_plan = CarePlan(**care_plan_data)
                
                logger.info(f"✅ Successfully generated care plan for diagnosis: {prescription.diagnosis}")
                return care_plan
                
            except json.JSONDecodeError as e:
                logger.error(f"❌ Failed to parse Bedrock response as JSON: {e}")
                logger.error(f"📄 Raw content preview: {content[:200]}...")
                # Fallback: create basic care plan
                return self._create_fallback_care_plan(prescription, content)
                
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            
            # DETAILED ERROR LOGGING
            logger.error("❌ === BEDROCK CLIENT ERROR DETAILS ===")
            logger.error(f"🚫 Error Code: {error_code}")
            logger.error(f"💬 Error Message: {error_message}")
            logger.error(f"🎯 Model ID Used: {model_id}")
            logger.error(f"🌍 Region: {self.bedrock_client._client_config.region_name}")
            logger.error(f"📦 Request Details: {e.response}")
            
            if error_code == 'AccessDeniedException':
                logger.error("🔒 ACCESS DENIED - Possible causes:")
                logger.error("   1. Model access not requested in Bedrock console")
                logger.error("   2. Payment method required for premium models")
                logger.error("   3. IAM permissions insufficient")
                logger.error("   4. Model not available in region")
                raise Exception("Access denied to Amazon Bedrock. Check IAM permissions.")
            elif error_code == 'ValidationException':
                logger.error("⚠️  VALIDATION ERROR - Possible causes:")
                logger.error("   1. Incorrect model ID format")
                logger.error("   2. Invalid request parameters")
                logger.error("   3. Model requires different API format")
                raise Exception("Invalid request to Bedrock. Check model ID and parameters.")
            else:
                logger.error(f"🔥 OTHER ERROR: {error_code}")
                raise Exception(f"Bedrock error: {error_code}")
                
        except Exception as e:
            logger.error("💥 === UNEXPECTED ERROR ===")
            logger.error(f"❌ Error Type: {type(e).__name__}")
            logger.error(f"💬 Error Message: {str(e)}")
            logger.error(f"🎯 Model ID: {model_id}")
            import traceback
            logger.error(f"📚 Traceback: {traceback.format_exc()}")
            raise Exception(f"Unexpected error in care plan generation: {str(e)}")
                
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
            bedrock_client = boto3.client('bedrock', region_name=self.bedrock_client._client_config.region_name)
            response = bedrock_client.list_foundation_models()
            
            # Filter for text generation models suitable for care plans
            suitable_models = []
            for model in response.get('modelSummaries', []):
                if 'TEXT' in model.get('outputModalities', []):
                    suitable_models.append(model['modelId'])
            
            return suitable_models
            
        except Exception as e:
            logger.error(f"Failed to list Bedrock models: {e}")
            # Return common model IDs as fallback including latest Claude models and Nova
            return [
                "anthropic.claude-sonnet-4-5-20250929-v1:0",
                "anthropic.claude-3-5-sonnet-20241022-v2:0", 
                "anthropic.claude-3-sonnet-20240229-v1:0",
                "anthropic.claude-3-haiku-20240307-v1:0",
                "amazon.titan-text-express-v1",
                "amazon.nova-micro-v1:0"
            ]

    def check_bedrock_access(self) -> Dict[str, Any]:
        """
        Check AWS Bedrock access and IAM permissions
        
        Returns:
            Dictionary with access check results
        """
        results = {
            "timestamp": datetime.now().isoformat(),
            "overall_access": False,
            "checks": {}
        }
        
        try:
            # Check 1: Basic bedrock client connection
            logger.info("🔍 === BEDROCK ACCESS CHECK ===")
            
            try:
                region = self.bedrock_client._client_config.region_name
                results["checks"]["bedrock_client"] = {
                    "status": "success",
                    "region": region,
                    "message": "Bedrock runtime client initialized successfully"
                }
                logger.info(f"✅ Bedrock client initialized in region: {region}")
            except Exception as e:
                results["checks"]["bedrock_client"] = {
                    "status": "error",
                    "message": f"Failed to initialize Bedrock client: {str(e)}"
                }
                logger.error(f"❌ Bedrock client initialization failed: {e}")
                return results
            
            # Check 2: List foundation models permission
            try:
                bedrock_admin_client = boto3.client('bedrock', region_name=region)
                response = bedrock_admin_client.list_foundation_models()
                model_count = len(response.get('modelSummaries', []))
                
                results["checks"]["list_models"] = {
                    "status": "success",
                    "model_count": model_count,
                    "message": f"Successfully listed {model_count} foundation models"
                }
                logger.info(f"✅ Listed {model_count} foundation models")
                
                # Extract available models
                available_models = [model['modelId'] for model in response.get('modelSummaries', [])]
                results["checks"]["list_models"]["available_models"] = available_models
                
            except ClientError as e:
                error_code = e.response['Error']['Code']
                results["checks"]["list_models"] = {
                    "status": "error",
                    "error_code": error_code,
                    "message": f"Failed to list models: {e.response['Error']['Message']}"
                }
                logger.error(f"❌ Failed to list models: {error_code}")
            
            # Check 3: Test basic model invocation with simple prompt
            test_models = [
                "anthropic.claude-3-haiku-20240307-v1:0",  # Standard model
                "anthropic.claude-3-sonnet-20240229-v1:0",  # Standard model
                "us.anthropic.claude-3-7-sonnet-20250219-v1:0",  # Latest standard inference profile
                "us.anthropic.claude-3-5-sonnet-20241022-v2:0",  # Inference profile
                "us.anthropic.claude-sonnet-4-5-20250929-v1:0",   # Premium inference profile
                "amazon.nova-micro-v1:0"  # Amazon Nova Micro
            ]
            
            results["checks"]["model_access"] = {}
            
            for model_id in test_models:
                try:
                    logger.info(f"🧪 Testing model access: {model_id}")
                    
                    # Prepare test body based on model type
                    if "amazon.nova" in model_id:
                        test_body = {
                            "messages": [
                                {
                                    "role": "user",
                                    "content": [
                                        {
                                            "text": "Say 'Hello'"
                                        }
                                    ]
                                }
                            ],
                            "inferenceConfig": {
                                "max_new_tokens": 10,
                                "temperature": 0.1
                            }
                        }
                    else:
                        # Claude format
                        test_body = {
                            "anthropic_version": "bedrock-2023-05-31",
                            "max_tokens": 10,
                            "messages": [
                                {
                                    "role": "user",
                                    "content": "Say 'Hello'"
                                }
                            ],
                            "temperature": 0.1
                        }
                    
                    response = self.bedrock_client.invoke_model(
                        modelId=model_id,
                        body=json.dumps(test_body),
                        contentType='application/json',
                        accept='application/json'
                    )
                    
                    # Parse response to verify it works
                    response_body = json.loads(response['body'].read())
                    
                    # Extract content based on model type
                    if "amazon.nova" in model_id:
                        content = response_body.get('output', {}).get('message', {}).get('content', [{}])[0].get('text', '')
                    else:
                        content = response_body.get('content', [{}])[0].get('text', '')
                    
                    results["checks"]["model_access"][model_id] = {
                        "status": "success",
                        "response_length": len(content),
                        "message": "Model accessible and responding",
                        "sample_response": content[:50] + "..." if len(content) > 50 else content
                    }
                    logger.info(f"✅ Model {model_id} accessible")
                    
                except ClientError as e:
                    error_code = e.response['Error']['Code']
                    error_message = e.response['Error']['Message']
                    
                    results["checks"]["model_access"][model_id] = {
                        "status": "error",
                        "error_code": error_code,
                        "message": error_message,
                        "details": self._analyze_model_error(error_code, error_message, model_id)
                    }
                    logger.error(f"❌ Model {model_id} access failed: {error_code}")
                
                except Exception as e:
                    results["checks"]["model_access"][model_id] = {
                        "status": "error",
                        "message": f"Unexpected error: {str(e)}"
                    }
                    logger.error(f"❌ Unexpected error testing {model_id}: {e}")
            
            # Check 4: AWS credentials information
            try:
                sts_client = boto3.client('sts', region_name=region)
                identity = sts_client.get_caller_identity()
                
                results["checks"]["aws_identity"] = {
                    "status": "success",
                    "account": identity.get('Account'),
                    "user_id": identity.get('UserId'),
                    "arn": identity.get('Arn'),
                    "message": "AWS identity retrieved successfully"
                }
                logger.info(f"✅ AWS Identity: {identity.get('Arn')}")
                
            except Exception as e:
                results["checks"]["aws_identity"] = {
                    "status": "error",
                    "message": f"Failed to get AWS identity: {str(e)}"
                }
                logger.error(f"❌ Failed to get AWS identity: {e}")
            
            # Determine overall access status
            successful_models = [
                model for model, result in results["checks"].get("model_access", {}).items()
                if result["status"] == "success"
            ]
            
            results["overall_access"] = len(successful_models) > 0
            results["summary"] = {
                "accessible_models": len(successful_models),
                "total_models_tested": len(test_models),
                "has_basic_access": results["checks"].get("bedrock_client", {}).get("status") == "success",
                "can_list_models": results["checks"].get("list_models", {}).get("status") == "success"
            }
            
            logger.info(f"🎯 Access check complete. Overall access: {results['overall_access']}")
            
        except Exception as e:
            logger.error(f"💥 Access check failed with unexpected error: {e}")
            results["checks"]["unexpected_error"] = {
                "status": "error",
                "message": f"Unexpected error during access check: {str(e)}"
            }
        
        return results
    
    def _analyze_model_error(self, error_code: str, error_message: str, model_id: str) -> Dict[str, str]:
        """
        Analyze model access errors and provide helpful guidance
        
        Args:
            error_code: AWS error code
            error_message: AWS error message
            model_id: Model ID that failed
            
        Returns:
            Dictionary with error analysis and recommendations
        """
        analysis = {
            "error_type": error_code,
            "likely_cause": "Unknown",
            "recommendation": "Check AWS documentation",
            "requires_action": "Unknown"
        }
        
        if error_code == 'AccessDeniedException':
            if 'inference profile' in error_message.lower():
                analysis.update({
                    "likely_cause": "Model requires inference profile access",
                    "recommendation": "Use inference profile ID (us.anthropic.* format) instead of direct model ID",
                    "requires_action": "Update model ID format"
                })
            elif 'payment' in error_message.lower() or 'billing' in error_message.lower():
                analysis.update({
                    "likely_cause": "Premium model requires payment method",
                    "recommendation": "Add payment method in AWS console for premium models",
                    "requires_action": "Configure billing"
                })
            else:
                analysis.update({
                    "likely_cause": "Insufficient IAM permissions or model access not requested",
                    "recommendation": "Check IAM permissions and request model access in Bedrock console",
                    "requires_action": "Update IAM or request access"
                })
        
        elif error_code == 'ValidationException':
            if 'throughput' in error_message.lower():
                analysis.update({
                    "likely_cause": "Model requires inference profile for on-demand access",
                    "recommendation": "Use inference profile ID (us.anthropic.* format)",
                    "requires_action": "Update model ID"
                })
            else:
                analysis.update({
                    "likely_cause": "Invalid model ID or request format",
                    "recommendation": "Check model ID format and request parameters",
                    "requires_action": "Fix model ID or request format"
                })
        
        elif error_code == 'ThrottlingException':
            analysis.update({
                "likely_cause": "Rate limit exceeded",
                "recommendation": "Implement retry logic with backoff",
                "requires_action": "Add rate limiting"
            })
        
        return analysis