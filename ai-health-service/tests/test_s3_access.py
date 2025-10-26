#!/usr/bin/env python3
"""
S3 Access Diagnostic Script
This script helps diagnose S3 access issues for the AI Health Service
"""

import os
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_aws_credentials():
    """Test AWS credentials and identity"""
    print("🔑 Testing AWS Credentials...")
    
    try:
        # Create STS client to test credentials
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        
        print(f"✅ AWS Identity confirmed:")
        print(f"   User ARN: {identity.get('Arn')}")
        print(f"   Account: {identity.get('Account')}")
        print(f"   User ID: {identity.get('UserId')}")
        return True
        
    except NoCredentialsError:
        print("❌ No AWS credentials found")
        print("   Check AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY")
        return False
    except ClientError as e:
        print(f"❌ AWS credential error: {e}")
        return False

def test_s3_bucket_access():
    """Test S3 bucket access and permissions"""
    bucket_name = os.getenv('S3_BUCKET_NAME')
    region = os.getenv('AWS_REGION', 'us-east-1')
    
    if not bucket_name:
        print("❌ S3_BUCKET_NAME not set in environment")
        return False
    
    print(f"\n🪣 Testing S3 Bucket Access: {bucket_name}")
    
    try:
        # Create S3 client
        s3 = boto3.client('s3', region_name=region)
        
        # Test 1: Check if bucket exists and get location
        print("   Testing bucket existence...")
        try:
            location = s3.get_bucket_location(Bucket=bucket_name)
            bucket_region = location.get('LocationConstraint') or 'us-east-1'
            print(f"   ✅ Bucket exists in region: {bucket_region}")
            
            if bucket_region != region:
                print(f"   ⚠️  Warning: Bucket region ({bucket_region}) != configured region ({region})")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'NoSuchBucket':
                print(f"   ❌ Bucket '{bucket_name}' does not exist")
                return False
            elif error_code == 'AccessDenied':
                print(f"   ❌ Access denied to bucket '{bucket_name}'")
                print("   Check bucket policy and IAM permissions")
                return False
            else:
                print(f"   ❌ Error checking bucket: {error_code}")
                return False
        
        # Test 2: Try to list bucket (requires ListBucket permission)
        print("   Testing ListBucket permission...")
        try:
            s3.list_objects_v2(Bucket=bucket_name, MaxKeys=1)
            print("   ✅ ListBucket permission confirmed")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            print(f"   ❌ ListBucket failed: {error_code}")
            if error_code == 'AccessDenied':
                print("   IAM user needs s3:ListBucket permission")
        
        # Test 3: Try to upload a test object (requires PutObject permission)
        print("   Testing PutObject permission...")
        test_key = "test-upload-diagnostic.txt"
        test_content = b"Test upload from AI Health Service diagnostic"
        
        try:
            s3.put_object(
                Bucket=bucket_name,
                Key=test_key,
                Body=test_content,
                ContentType='text/plain'
            )
            print("   ✅ PutObject permission confirmed")
            
            # Clean up test object
            try:
                s3.delete_object(Bucket=bucket_name, Key=test_key)
                print("   ✅ Test object cleaned up")
            except:
                print(f"   ⚠️  Could not delete test object: {test_key}")
                
        except ClientError as e:
            error_code = e.response['Error']['Code']
            print(f"   ❌ PutObject failed: {error_code}")
            if error_code == 'AccessDenied':
                print("   IAM user needs s3:PutObject permission")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Unexpected S3 error: {e}")
        return False

def check_environment_variables():
    """Check required environment variables"""
    print("\n📋 Checking Environment Variables...")
    
    required_vars = [
        'AWS_ACCESS_KEY_ID',
        'AWS_SECRET_ACCESS_KEY',
        'AWS_REGION',
        'S3_BUCKET_NAME'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            if 'KEY' in var:
                display_value = value[:4] + '*' * (len(value) - 8) + value[-4:]
            else:
                display_value = value
            print(f"   ✅ {var}: {display_value}")
        else:
            print(f"   ❌ {var}: Not set")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n❌ Missing required environment variables: {', '.join(missing_vars)}")
        return False
    
    return True

def print_iam_policy_suggestion():
    """Print suggested IAM policy for S3 access"""
    bucket_name = os.getenv('S3_BUCKET_NAME')
    
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "s3:PutObject",
                    "s3:PutObjectAcl",
                    "s3:GetObject",
                    "s3:ListBucket"
                ],
                "Resource": [
                    f"arn:aws:s3:::{bucket_name}",
                    f"arn:aws:s3:::{bucket_name}/*"
                ]
            }
        ]
    }
    
    print("\n📋 Suggested IAM Policy:")
    print("=" * 50)
    import json
    print(json.dumps(policy, indent=2))
    print("=" * 50)

def main():
    """Main diagnostic function"""
    print("🏥 AI Health Service - S3 Access Diagnostic")
    print("=" * 50)
    
    # Check environment variables
    if not check_environment_variables():
        return False
    
    # Test AWS credentials
    if not test_aws_credentials():
        return False
    
    # Test S3 access
    if not test_s3_bucket_access():
        print_iam_policy_suggestion()
        return False
    
    print("\n🎉 All S3 access tests passed!")
    print("Your AI Health Service should be able to upload files to S3.")
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)