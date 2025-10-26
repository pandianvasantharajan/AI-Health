#!/usr/bin/env python3
"""
Care Plan Module Test Script
Tests the care plan functionality without requiring Bedrock access
"""

import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def test_endpoint(endpoint: str, method: str = "GET", data: Dict[Any, Any] = None) -> Dict[Any, Any]:
    """Test an API endpoint"""
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
            "data": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def main():
    """Run care plan module tests"""
    print("🏥 AI Health Service - Care Plan Module Tests")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1. Testing health check...")
    result = test_endpoint("/health")
    if result["success"]:
        print("✅ Health check passed")
    else:
        print(f"❌ Health check failed: {result}")
        return
    
    # Test 2: Demo care plan (no Bedrock required)
    print("\n2. Testing demo care plan generation...")
    result = test_endpoint("/care-plan/demo", "POST")
    if result["success"]:
        care_plan = result["data"]["care_plan"]
        print("✅ Demo care plan generated successfully")
        print(f"   Patient Summary: {care_plan['patient_summary'][:100]}...")
        print(f"   Care Goals: {len(care_plan['care_goals'])} goals")
        print(f"   Medication Management: {len(care_plan['medication_management'])} sections")
        print(f"   Warning Signs: {len(care_plan['warning_signs'])} signs")
    else:
        print(f"❌ Demo care plan failed: {result}")
    
    # Test 3: Available models
    print("\n3. Testing available models...")
    result = test_endpoint("/care-plan/models")
    if result["success"]:
        models = result["data"]["available_models"]
        print(f"✅ Found {len(models)} available models")
        print(f"   Default model: {result['data']['current_default']}")
        for model in models:
            print(f"   - {model}")
    else:
        print(f"❌ Models list failed: {result}")
    
    # Test 4: Custom care plan generation (structure test)
    print("\n4. Testing custom prescription structure...")
    
    sample_prescription = {
        "patient_info": {
            "age": 35,
            "gender": "Male",
            "weight": 75.0,
            "medical_conditions": ["Asthma"],
            "allergies": ["Shellfish"]
        },
        "diagnosis": "Acute respiratory infection",
        "prescriptions": [
            {
                "medication_name": "Azithromycin",
                "dosage": "500mg daily",
                "duration": "5 days",
                "instructions": "Take on empty stomach"
            },
            {
                "medication_name": "Albuterol inhaler",
                "dosage": "2 puffs every 4 hours as needed",
                "duration": "30 days",
                "instructions": "For shortness of breath"
            }
        ],
        "doctor_notes": "Monitor for improvement in 3-5 days"
    }
    
    # This will fail due to Bedrock access, but shows the structure
    result = test_endpoint("/care-plan/generate", "POST", sample_prescription)
    if result["success"]:
        print("✅ Custom care plan generated (Bedrock working!)")
    else:
        print("⚠️  Custom care plan failed (expected - requires Bedrock setup)")
        print("   This is normal if Bedrock access is not configured")
        print("   Use the demo endpoint to see the expected structure")
    
    # Test 5: Sample care plan (with Bedrock)
    print("\n5. Testing sample care plan...")
    result = test_endpoint("/care-plan/sample", "POST")
    if result["success"]:
        print("✅ Sample care plan generated (Bedrock working!)")
    else:
        print("⚠️  Sample care plan failed (expected - requires Bedrock setup)")
        print("   This is normal if Bedrock access is not configured")
    
    print("\n" + "=" * 50)
    print("🎉 Care Plan Module Tests Complete!")
    print("\nNext Steps:")
    print("1. Configure Bedrock access for AI-generated care plans")
    print("2. Visit http://localhost:8000/docs for interactive API testing")
    print("3. Use /care-plan/demo to see the expected structure")
    print("4. Refer to CARE_PLAN_GUIDE.md for setup instructions")

if __name__ == "__main__":
    main()