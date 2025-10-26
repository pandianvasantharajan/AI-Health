# S3 Access Denied - Solution Guide

## Problem Identified ✅

The diagnostic script confirmed that:
- ✅ AWS credentials are valid and working
- ✅ Environment variables are properly configured
- ❌ IAM user `vasantharajan` lacks S3 permissions for bucket `ai-health-demo-bucket`

## Solutions (Choose One)

### Option 1: Add IAM Policy to Existing User (Recommended)

1. **Go to AWS Console → IAM → Users → vasantharajan**

2. **Click "Add permissions" → "Attach policies directly"**

3. **Create a custom policy with this JSON:**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket",
        "s3:GetBucketLocation"
      ],
      "Resource": "arn:aws:s3:::ai-health-demo-bucket"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:PutObjectAcl",
        "s3:GetObject",
        "s3:DeleteObject"
      ],
      "Resource": "arn:aws:s3:::ai-health-demo-bucket/*"
    }
  ]
}
```

### Option 2: Create the S3 Bucket

If the bucket doesn't exist, create it:

1. **Go to AWS Console → S3**
2. **Click "Create bucket"**
3. **Name:** `ai-health-demo-bucket`
4. **Region:** `us-east-1` (to match your config)
5. **Keep default settings and create**

### Option 3: Use an Existing Bucket

Update your `.env` file with a bucket you already have access to:

```bash
# Change this line in .env
S3_BUCKET_NAME=your-existing-bucket-name
```

## Test the Fix

After applying any solution, restart the service and test:

```bash
# Restart the service
docker-compose restart

# Test S3 access
docker-compose exec ai-health-service python test_s3_access.py

# Test the upload endpoint
curl -X POST "http://localhost:8000/upload/pdf" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@test-document.pdf"
```

## Security Note ⚠️

Your AWS credentials were visible in the .env file. For better security:

1. **Rotate your AWS access keys:**
   - Go to IAM → Users → vasantharajan → Security credentials
   - Create new access key
   - Delete the old one
   - Update your .env file

2. **Never commit .env files to git** (already handled in this repo)

## Next Steps

1. Choose one of the solutions above
2. Test with the diagnostic script
3. Try uploading a file through the API
4. Consider rotating your AWS credentials

The most common solution is **Option 1** - adding the IAM policy to your existing user.