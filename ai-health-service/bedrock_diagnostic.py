#!/usr/bin/env python3
"""
Amazon Bedrock Access Diagnostic Script
Helps identify and resolve Bedrock access issues
"""

import boto3
import json
import os
from botocore.exceptions import ClientError, NoCredentialsError, ProfileNotFound

def check_aws_credentials():
    """Check if AWS credentials are properly configured"""
    print("🔐 Checking AWS Credentials...")
    
    try:
        # Try to create a boto3 session
        session = boto3.Session()
        credentials = session.get_credentials()
        
        if credentials is None:
            print("❌ No AWS credentials found")
            return False
        
        print(f"✅ Credentials found:")
        print(f"   Access Key ID: {credentials.access_key[:10]}...")
        print(f"   Region: {session.region_name or 'Not set'}")
        
        # Test basic AWS access
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        print(f"   User ARN: {identity.get('Arn')}")
        print(f"   Account ID: {identity.get('Account')}")
        
        return True
        
    except NoCredentialsError:
        print("❌ AWS credentials not configured")
        return False
    except Exception as e:
        print(f"❌ Error checking credentials: {e}")
        return False

def check_bedrock_availability():
    """Check if Bedrock is available in the region"""
    print("\n🌍 Checking Bedrock Region Availability...")
    
    region = os.getenv('BEDROCK_REGION', 'us-east-1')
    print(f"   Checking region: {region}")
    
    # Bedrock is available in these regions as of 2024
    bedrock_regions = [
        'us-east-1',    # N. Virginia
        'us-west-2',    # Oregon  
        'ap-southeast-1', # Singapore
        'ap-northeast-1', # Tokyo
        'eu-west-1',    # Ireland
        'eu-central-1', # Frankfurt
    ]
    
    if region in bedrock_regions:
        print(f"✅ Bedrock is available in {region}")
        return True
    else:
        print(f"❌ Bedrock may not be available in {region}")
        print(f"   Available regions: {', '.join(bedrock_regions)}")
        return False

def check_bedrock_service_access():
    """Test basic Bedrock service access"""
    print("\n🤖 Testing Bedrock Service Access...")
    
    try:
        region = os.getenv('BEDROCK_REGION', 'us-east-1')
        bedrock = boto3.client('bedrock', region_name=region)
        
        # Try to list foundation models (this requires bedrock:ListFoundationModels)
        response = bedrock.list_foundation_models()
        print(f"✅ Bedrock service accessible")
        print(f"   Found {len(response['modelSummaries'])} foundation models")
        
        # Check if our specific model is available
        model_id = os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3-sonnet-20240229-v1:0')
        available_models = [model['modelId'] for model in response['modelSummaries']]
        
        if model_id in available_models:
            print(f"✅ Target model {model_id} is available")
        else:
            print(f"❌ Target model {model_id} not found")
            print(f"   Available Claude models:")
            claude_models = [m for m in available_models if 'claude' in m.lower()]
            for model in claude_models[:5]:  # Show first 5
                print(f"     - {model}")
        
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        print(f"❌ Bedrock service access failed:")
        print(f"   Error Code: {error_code}")
        print(f"   Error Message: {error_message}")
        
        if error_code == 'AccessDeniedException':
            print(f"   🔧 This indicates insufficient IAM permissions for Bedrock")
        elif error_code == 'UnauthorizedOperation':
            print(f"   🔧 Check if Bedrock is enabled in your AWS account")
        
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def check_bedrock_runtime_access():
    """Test Bedrock Runtime access (needed for inference)"""
    print("\n⚡ Testing Bedrock Runtime Access...")
    
    try:
        region = os.getenv('BEDROCK_REGION', 'us-east-1')
        bedrock_runtime = boto3.client('bedrock-runtime', region_name=region)
        
        # Try a simple inference call with minimal payload
        model_id = os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3-sonnet-20240229-v1:0')
        
        # Minimal test payload for Claude
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 10,
            "messages": [
                {
                    "role": "user",
                    "content": "Hello"
                }
            ]
        })
        
        response = bedrock_runtime.invoke_model(
            body=body,
            modelId=model_id,
            accept='application/json',
            contentType='application/json'
        )
        
        print(f"✅ Bedrock Runtime access successful")
        print(f"   Model {model_id} responded correctly")
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        print(f"❌ Bedrock Runtime access failed:")
        print(f"   Error Code: {error_code}")
        print(f"   Error Message: {error_message}")
        
        if error_code == 'AccessDeniedException':
            print(f"   🔧 Missing bedrock:InvokeModel permission")
        elif error_code == 'ValidationException':
            print(f"   🔧 Model may not be available or request format incorrect")
        elif error_code == 'ResourceNotFoundException':
            print(f"   🔧 Model {model_id} not found - check model ID")
        
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def check_model_access():
    """Check access to the specific model we're trying to use"""
    print("\n🎯 Checking Specific Model Access...")
    
    model_id = os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3-sonnet-20240229-v1:0')
    region = os.getenv('BEDROCK_REGION', 'us-east-1')
    
    print(f"   Target Model: {model_id}")
    print(f"   Region: {region}")
    
    try:
        bedrock = boto3.client('bedrock', region_name=region)
        
        # Get specific model details
        response = bedrock.get_foundation_model(modelIdentifier=model_id)
        model_details = response['modelDetails']
        
        print(f"✅ Model details retrieved:")
        print(f"   Model Name: {model_details['modelName']}")
        print(f"   Provider: {model_details['providerName']}")
        print(f"   Input Modalities: {model_details['inputModalities']}")
        print(f"   Output Modalities: {model_details['outputModalities']}")
        
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        print(f"❌ Cannot access model {model_id}:")
        print(f"   Error: {error_code}")
        
        if error_code == 'ResourceNotFoundException':
            print(f"   🔧 Model not found - check model ID spelling and availability")
        
        return False

def provide_recommendations():
    """Provide specific recommendations based on findings"""
    print("\n💡 Troubleshooting Recommendations:")
    print("\n1. **Check Model Access in AWS Console:**")
    print("   - Go to AWS Bedrock console")
    print("   - Navigate to 'Foundation models'")
    print("   - Check if Claude 3 Sonnet is 'Available' (not just 'Enabled')")
    print("   - If not available, request model access")
    
    print("\n2. **Verify IAM Permissions:**")
    print("   Your user/role needs these specific permissions:")
    print("   - bedrock:ListFoundationModels")
    print("   - bedrock:GetFoundationModel") 
    print("   - bedrock:InvokeModel")
    print("   - bedrock:InvokeModelWithResponseStream")
    
    print("\n3. **Check Service Enablement:**")
    print("   - Bedrock might need to be explicitly enabled in your account")
    print("   - Some regions require manual service activation")
    
    print("\n4. **Verify Model Availability:**")
    print("   - Claude 3 models require explicit access request")
    print("   - Check Bedrock console for model access status")
    
    print("\n5. **Test with AWS CLI:**")
    print("   Run this command to test directly:")
    print("   aws bedrock list-foundation-models --region us-east-1")

def main():
    """Run comprehensive Bedrock diagnostics"""
    print("🔍 Amazon Bedrock Access Diagnostics")
    print("=" * 50)
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    all_checks_passed = True
    
    # Run all diagnostic checks
    checks = [
        check_aws_credentials,
        check_bedrock_availability, 
        check_bedrock_service_access,
        check_bedrock_runtime_access,
        check_model_access
    ]
    
    for check in checks:
        try:
            if not check():
                all_checks_passed = False
        except Exception as e:
            print(f"❌ Check failed with error: {e}")
            all_checks_passed = False
    
    print("\n" + "=" * 50)
    if all_checks_passed:
        print("🎉 All checks passed! Bedrock should be working.")
    else:
        print("⚠️  Some checks failed. See recommendations below.")
        provide_recommendations()
    
    print(f"\n🌐 Service URL: http://localhost:8000")
    print(f"📚 Try again: curl -X POST http://localhost:8000/care-plan/sample")

if __name__ == "__main__":
    main()