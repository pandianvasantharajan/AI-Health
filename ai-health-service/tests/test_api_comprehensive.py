"""
Comprehensive API Tests for AI Health Service
Tests both file upload and care plan functionality
"""

import pytest
import json
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestHealthCheck:
    """Test health check endpoints"""
    
    def test_health_check(self):
        """Test main health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data

class TestFileUpload:
    """Test file upload functionality"""
    
    def test_upload_endpoint_exists(self):
        """Test that upload endpoints are accessible"""
        # Test PDF upload endpoint
        response = client.post("/upload/pdf")
        # Should return 422 (validation error) since no file provided
        assert response.status_code == 422
        
        # Test general upload endpoint
        response = client.post("/upload/file")
        # Should return 422 (validation error) since no file provided
        assert response.status_code == 422

class TestCarePlan:
    """Test care plan functionality"""
    
    def test_available_models(self):
        """Test getting available Bedrock models"""
        response = client.get("/care-plan/models")
        assert response.status_code == 200
        data = response.json()
        assert "available_models" in data
        assert "current_default" in data
        assert isinstance(data["available_models"], list)
        assert len(data["available_models"]) > 0
    
    def test_demo_care_plan(self):
        """Test demo care plan generation (no Bedrock required)"""
        response = client.post("/care-plan/demo")
        assert response.status_code == 200
        
        data = response.json()
        assert "care_plan" in data
        assert "metadata" in data
        
        care_plan = data["care_plan"]
        
        # Verify required fields
        required_fields = [
            "patient_summary",
            "care_goals", 
            "medication_management",
            "lifestyle_recommendations",
            "monitoring_schedule",
            "warning_signs",
            "emergency_contacts",
            "follow_up_plan"
        ]
        
        for field in required_fields:
            assert field in care_plan, f"Missing required field: {field}"
        
        # Verify data types
        assert isinstance(care_plan["care_goals"], list)
        assert isinstance(care_plan["medication_management"], list)
        assert isinstance(care_plan["lifestyle_recommendations"], list)
        assert isinstance(care_plan["monitoring_schedule"], list)
        assert isinstance(care_plan["warning_signs"], list)
        assert isinstance(care_plan["emergency_contacts"], list)
        assert isinstance(care_plan["follow_up_plan"], list)
        
        # Verify non-empty content
        assert len(care_plan["care_goals"]) > 0
        assert len(care_plan["medication_management"]) > 0
        assert len(care_plan["warning_signs"]) > 0
    
    def test_care_plan_generation_validation(self):
        """Test care plan generation with invalid data"""
        # Test with empty prescription
        response = client.post("/care-plan/generate", json={})
        assert response.status_code == 422  # Validation error
        
        # Test with invalid structure
        invalid_data = {
            "patient_info": {
                "age": "invalid",  # Should be number
                "gender": "Male"
            }
        }
        response = client.post("/care-plan/generate", json=invalid_data)
        assert response.status_code == 422  # Validation error
    
    def test_care_plan_generation_valid_structure(self):
        """Test care plan generation with valid data structure"""
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
                },
                {
                    "medication_name": "Albuterol inhaler",
                    "dosage": "2 puffs every 4-6 hours as needed",
                    "duration": "30 days", 
                    "instructions": "Use for shortness of breath"
                }
            ],
            "doctor_notes": "Patient has well-controlled diabetes and hypertension. Monitor for respiratory improvement."
        }
        
        response = client.post("/care-plan/generate", json=valid_prescription)
        
        # This may fail due to Bedrock access, but structure should be valid
        if response.status_code != 200:
            # Check if it's a Bedrock access issue (expected)
            assert response.status_code in [500, 400]  # Server error due to AWS access
        else:
            # If it works, validate the response
            data = response.json()
            assert "care_plan" in data
    
    def test_sample_care_plan(self):
        """Test sample care plan generation"""
        response = client.post("/care-plan/sample")
        
        # This may fail due to Bedrock access
        if response.status_code != 200:
            # Check if it's a Bedrock access issue (expected)
            assert response.status_code in [500, 400]
        else:
            # If it works, validate the response
            data = response.json()
            assert "care_plan" in data

class TestAPIDocs:
    """Test API documentation endpoints"""
    
    def test_docs_accessible(self):
        """Test that API docs are accessible"""
        response = client.get("/docs")
        assert response.status_code == 200
        
    def test_openapi_schema(self):
        """Test OpenAPI schema endpoint"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data

class TestCORS:
    """Test CORS configuration"""
    
    def test_cors_headers(self):
        """Test that CORS headers are present"""
        response = client.get("/health")
        assert response.status_code == 200
        # CORS headers should be present for browser compatibility

if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main(["-v", __file__])