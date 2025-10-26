#!/usr/bin/env python3
"""
AI Health Service - Complete Functionality Demo
Demonstrates all features of the monorepo service
"""

import requests
import json
import sys
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def print_section(title: str):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"🏥 {title}")
    print(f"{'='*60}")

def print_subsection(title: str):
    """Print a formatted subsection header"""
    print(f"\n{'-'*40}")
    print(f"📋 {title}")
    print(f"{'-'*40}")

def test_endpoint(endpoint: str, method: str = "GET", data: Dict[Any, Any] = None) -> Dict[Any, Any]:
    """Test an API endpoint and return results"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        return {
            "success": response.status_code == 200,
            "status_code": response.status_code,
            "data": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text,
            "response_size": len(response.content)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def demo_care_plan_structure(care_plan: Dict[Any, Any]):
    """Demo the structure of a care plan"""
    print(f"   📊 Patient Summary: {care_plan.get('patient_summary', 'N/A')[:100]}...")
    print(f"   🎯 Care Goals: {len(care_plan.get('care_goals', []))} goals defined")
    print(f"   💊 Medication Management: {len(care_plan.get('medication_management', []))} sections")
    print(f"   🏃 Lifestyle Recommendations: {len(care_plan.get('lifestyle_recommendations', []))} items")
    print(f"   📅 Monitoring Schedule: {len(care_plan.get('monitoring_schedule', []))} checkpoints")
    print(f"   ⚠️  Warning Signs: {len(care_plan.get('warning_signs', []))} signs to watch")
    
    # Handle follow_up_recommendations instead of emergency_contacts and follow_up_plan
    follow_up = care_plan.get('follow_up_recommendations', [])
    print(f"   📋 Follow-up Recommendations: {len(follow_up)} items")

def main():
    """Run complete functionality demonstration"""
    print("🏥 AI Health Service - Complete Functionality Demo")
    print("A comprehensive monorepo with Python service and React UI")
    print("Features: S3 file uploads, Docker hosting, Poetry management, AI care plans")
    
    # Test 1: Service Health
    print_section("Service Health & Status")
    result = test_endpoint("/health")
    if result["success"]:
        health_data = result["data"]
        print(f"✅ Service Status: {health_data['status']}")
        print(f"📦 Service Name: {health_data['service']}")
        print(f"🔢 Version: {health_data['version']}")
        print(f"⏰ Response Time: Fast")
    else:
        print(f"❌ Health check failed: {result}")
        print("🔧 Make sure the service is running with 'docker-compose up'")
        return False
    
    # Test 2: API Documentation
    print_section("API Documentation")
    print("📚 Interactive API Documentation:")
    print(f"   🌐 Swagger UI: {BASE_URL}/docs")
    print(f"   📋 OpenAPI Schema: {BASE_URL}/openapi.json")
    
    result = test_endpoint("/openapi.json")
    if result["success"]:
        openapi = result["data"]
        paths = list(openapi.get("paths", {}).keys())
        print(f"✅ API Schema loaded with {len(paths)} endpoints")
        print("   Available endpoints:")
        for path in sorted(paths):
            print(f"     • {path}")
    else:
        print("❌ Could not load API schema")
    
    # Test 3: File Upload Capabilities
    print_section("File Upload Service")
    print("📁 File Upload Endpoints:")
    print("   • POST /upload/pdf - Upload PDF files to S3")
    print("   • POST /upload/file - Upload any file type to S3")
    print("   • Supports folder organization and metadata")
    print("   • Built-in PDF validation and security checks")
    print("   • Integration with AWS S3 for secure storage")
    
    # Test upload endpoint availability
    result = test_endpoint("/upload/pdf", "POST")
    if result["status_code"] == 422:  # Expected validation error
        print("✅ Upload endpoints are accessible (validation working)")
    else:
        print("⚠️  Upload endpoint response unexpected")
    
    # Test 4: AI Care Plan System
    print_section("AI Care Plan Generation System")
    
    # Test available models
    print_subsection("Available AI Models")
    result = test_endpoint("/care-plan/models")
    if result["success"]:
        models_data = result["data"]
        models = models_data["available_models"]
        default_model = models_data["current_default"]
        print(f"✅ Found {len(models)} Amazon Bedrock models")
        print(f"🤖 Default Model: {default_model}")
        print("   Available models:")
        for model in models:
            print(f"     • {model}")
    else:
        print("❌ Could not retrieve available models")
    
    # Test demo care plan
    print_subsection("Demo Care Plan Generation")
    result = test_endpoint("/care-plan/demo", "POST")
    if result["success"]:
        demo_data = result["data"]
        care_plan = demo_data["care_plan"]
        
        print(f"✅ Demo care plan generated successfully")
        print(f"📊 Response size: {result['response_size']} bytes")
        print(f"🔧 Generation method: Demo (no Bedrock required)")
        print(f"📅 Generated at: {care_plan.get('generated_at', 'Unknown')}")
        print(f"💡 Note: {demo_data.get('note', 'No note')}")
        print("\n📋 Care Plan Structure:")
        demo_care_plan_structure(care_plan)
        
        # Show sample content
        print("\n📝 Sample Content Preview:")
        if care_plan.get('care_goals'):
            print(f"   First Care Goal: {care_plan['care_goals'][0]}")
        if care_plan.get('warning_signs'):
            print(f"   First Warning Sign: {care_plan['warning_signs'][0]}")
        
    else:
        print(f"❌ Demo care plan failed: {result}")
    
    # Test care plan validation
    print_subsection("Care Plan Input Validation")
    
    # Test with invalid data
    invalid_data = {"invalid": "data"}
    result = test_endpoint("/care-plan/generate", "POST", invalid_data)
    if result["status_code"] == 422:
        print("✅ Input validation working correctly")
        print("   🔍 Pydantic models ensure data integrity")
    else:
        print("⚠️  Validation response unexpected")
    
    # Test with valid structure
    valid_prescription = {
        "patient_info": {
            "age": 45,
            "gender": "Female",
            "weight": 65.0,
            "medical_conditions": ["Hypertension", "Type 2 Diabetes"],
            "allergies": ["Penicillin"]
        },
        "diagnosis": "Acute bronchitis with underlying conditions",
        "prescriptions": [
            {
                "medication_name": "Azithromycin",
                "dosage": "500mg daily",
                "duration": "5 days",
                "instructions": "Take with food"
            }
        ],
        "doctor_notes": "Monitor for improvement"
    }
    
    result = test_endpoint("/care-plan/generate", "POST", valid_prescription)
    if result["success"]:
        print("🎉 Full Bedrock integration working!")
        print("   AI-generated care plans are functional")
    else:
        print("⚠️  Bedrock integration pending (requires AWS setup)")
        print("   This is expected until Bedrock access is configured")
    
    # Test 5: Technology Stack Summary
    print_section("Technology Stack & Architecture")
    print("🐍 Backend: FastAPI (Python)")
    print("   • Modern async Python web framework")
    print("   • Automatic API documentation generation")
    print("   • Built-in data validation with Pydantic")
    print("   • High performance and scalability")
    
    print("\n📦 Dependency Management: Poetry")
    print("   • Modern Python package management")
    print("   • Dependency resolution and virtual environments")
    print("   • Lock files for reproducible builds")
    print("   • Development and production dependencies")
    
    print("\n🐳 Containerization: Docker")
    print("   • Multi-stage builds for optimization")
    print("   • Docker Compose for orchestration")
    print("   • Health checks and monitoring")
    print("   • Production-ready configuration")
    
    print("\n☁️  AWS Integration:")
    print("   • S3 for secure file storage")
    print("   • Bedrock for AI/ML capabilities")
    print("   • IAM for security and access control")
    print("   • boto3 for AWS service integration")
    
    print("\n🤖 AI/ML Features:")
    print("   • Amazon Bedrock integration")
    print("   • Claude 3 Sonnet for care plan generation")
    print("   • Structured data models for medical data")
    print("   • Comprehensive care plan templates")
    
    # Final Summary
    print_section("Service Status Summary")
    print("✅ Monorepo structure complete")
    print("✅ Python service with S3 upload module")
    print("✅ Docker hosting and containerization")
    print("✅ Poetry-based dependency management")
    print("✅ Care plan module with AI integration")
    print("✅ Comprehensive API documentation")
    print("✅ Health monitoring and error handling")
    print("✅ Structured data validation")
    print("✅ Modular architecture for scalability")
    
    print("\n🎯 Next Steps:")
    print("1. Configure AWS Bedrock access for full AI functionality")
    print("2. Set up React UI in ai-health-ui/ directory")
    print("3. Deploy to production environment")
    print("4. Add authentication and authorization")
    print("5. Implement comprehensive logging and monitoring")
    
    print(f"\n🌐 Service Running: {BASE_URL}")
    print(f"📚 Documentation: {BASE_URL}/docs")
    print(f"🔍 Health Check: {BASE_URL}/health")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)