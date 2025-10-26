#!/bin/bash
# Claude Sonnet 4.5 Payment Activation Monitor

echo "🔍 Monitoring Claude Sonnet 4.5 Payment Activation..."
echo "💳 Payment method added - waiting for AWS activation"
echo "⏰ Started at: $(date)"
echo ""

# Function to test Claude Sonnet 4.5 access
test_claude_access() {
    echo "🧪 Testing Claude Sonnet 4.5 access..."
    
    # Test the service endpoint
    response=$(curl -s http://localhost:8000/care-plan/sample -X POST)
    
    # Check if it's working
    if echo "$response" | grep -q '"care_plan"'; then
        echo "🎉 SUCCESS! Claude Sonnet 4.5 is working!"
        echo "💳 Payment method successfully activated!"
        echo ""
        echo "📊 Testing response size..."
        echo "$response" | python -c "
import json, sys
try:
    data = json.load(sys.stdin)
    care_plan = data['care_plan']
    print(f'✅ Care Plan Generated: {len(json.dumps(data))} bytes')
    print(f'👤 Patient Summary: {care_plan[\"patient_summary\"][:100]}...')
    print(f'🎯 Care Goals: {len(care_plan[\"care_goals\"])} goals')
    print(f'💊 Medication Items: {len(care_plan[\"medication_management\"])} items')
except:
    print('Response generated but could not parse details')
"
        return 0
    elif echo "$response" | grep -q "INVALID_PAYMENT_INSTRUMENT"; then
        echo "⏳ Payment still processing..."
        return 1
    elif echo "$response" | grep -q "Access denied"; then
        echo "🔧 Still getting access denied - may need more time"
        return 1
    else
        echo "⚠️  Unexpected response:"
        echo "$response" | head -3
        return 1
    fi
}

# Test immediately first
if test_claude_access; then
    echo ""
    echo "🚀 Your AI Health Service is ready for production!"
    echo "🤖 Claude Sonnet 4.5 premium AI generation is active!"
    echo ""
    echo "🧪 Test commands:"
    echo "  curl -X POST http://localhost:8000/care-plan/sample"
    echo "  curl -X POST http://localhost:8000/care-plan/generate -H 'Content-Type: application/json' -d '{...}'"
    exit 0
fi

echo ""
echo "⏰ Waiting for payment activation..."
echo "💡 AWS typically takes 5-15 minutes to process payment methods"
echo "🔄 Will check every 2 minutes..."
echo ""

# Wait and retry every 2 minutes for up to 20 minutes
for i in {1..10}; do
    echo "📅 Check #$i at $(date '+%H:%M:%S')"
    
    if test_claude_access; then
        echo ""
        echo "🎉 ACTIVATION COMPLETE!"
        echo "⏱️  Total wait time: $(($i * 2)) minutes"
        echo ""
        echo "🚀 Your AI Health Service is ready!"
        echo "🤖 Claude Sonnet 4.5 premium AI generation is active!"
        echo ""
        echo "🧪 Available endpoints:"
        echo "  • POST /care-plan/sample (AI-generated sample)"
        echo "  • POST /care-plan/generate (custom prescriptions)"
        echo "  • POST /care-plan/demo (always working demo)"
        echo "  • GET  /care-plan/models (model information)"
        break
    fi
    
    if [ $i -lt 10 ]; then
        echo "   ⏳ Waiting 2 minutes before next check..."
        sleep 120
    fi
done

if [ $i -eq 10 ]; then
    echo ""
    echo "⚠️  Payment activation taking longer than expected"
    echo "💡 Possible solutions:"
    echo "   1. Check AWS Billing Console for any issues"
    echo "   2. Verify credit card is valid and not expired"
    echo "   3. Contact AWS support if payment method shows as active"
    echo "   4. Try again in a few more minutes"
fi

echo ""
echo "📊 Current service status:"
curl -s http://localhost:8000/health | python -m json.tool