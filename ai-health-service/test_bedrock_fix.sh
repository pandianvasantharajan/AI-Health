#!/bin/bash
# Test Bedrock access after model approval

echo "🧪 Testing Bedrock Access After Model Approval..."

# Test the care plan endpoint
echo "📋 Testing care plan sample endpoint..."
curl -X POST http://localhost:8000/care-plan/sample -H "Content-Type: application/json" | jq '.'

echo -e "\n📋 Testing care plan generation endpoint..."
curl -X POST http://localhost:8000/care-plan/generate \
  -H "Content-Type: application/json" \
  -d '{
    "patient_info": {
      "age": 45,
      "gender": "Female",
      "medical_conditions": ["Hypertension"]
    },
    "diagnosis": "Acute bronchitis",
    "prescriptions": [{
      "medication_name": "Azithromycin",
      "dosage": "500mg daily",
      "duration": "5 days",
      "instructions": "Take with food"
    }],
    "doctor_notes": "Monitor for improvement"
  }' | jq '.'

echo -e "\n✅ If both commands return care plans, Bedrock is working!"
echo "🎉 Your AI Health Service is fully functional!"