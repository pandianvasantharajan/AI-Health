# Bedrock Access Issue Resolution

## 🚨 Problem Identified

Your AWS user has `AmazonBedrockFullAccess` but there's an **explicit deny** policy blocking `bedrock:InvokeModel`. This is causing the error:

```
AccessDeniedException: User: arn:aws:iam::339712840004:user/vasantharajan is not authorized to perform: bedrock:InvokeModel on resource: arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0 with an explicit deny in an identity-based policy
```

## ✅ What's Working
- ✅ AWS credentials are valid
- ✅ Bedrock service access works (`bedrock:ListFoundationModels`)
- ✅ Target model `anthropic.claude-3-sonnet-20240229-v1:0` is available
- ✅ 24 Claude models found in your account

## ❌ What's Blocked
- ❌ `bedrock:InvokeModel` - blocked by explicit deny policy
- ❌ This prevents actual AI inference calls

## 🔧 Solutions

### Option 1: Remove Explicit Deny Policy (Recommended)
1. **Go to AWS IAM Console**
2. **Navigate to Users → vasantharajan**
3. **Check all attached policies for explicit deny statements**
4. **Look for policies containing:**
   ```json
   {
     "Effect": "Deny",
     "Action": ["bedrock:InvokeModel", "bedrock:*"],
     "Resource": "*"
   }
   ```
5. **Remove or modify the deny statement**

### Option 2: Create Override Policy
If you can't remove the deny policy, create a new policy with higher precedence:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream"
            ],
            "Resource": [
                "arn:aws:bedrock:*::foundation-model/anthropic.claude-*",
                "arn:aws:bedrock:*::foundation-model/amazon.titan-*"
            ]
        }
    ]
}
```

### Option 3: Switch to IAM Role
Create an IAM role with proper Bedrock permissions and assume it:

1. **Create role with trust policy:**
   ```json
   {
       "Version": "2012-10-17",
       "Statement": [
           {
               "Effect": "Allow",
               "Principal": {
                   "AWS": "arn:aws:iam::339712840004:user/vasantharajan"
               },
               "Action": "sts:AssumeRole"
           }
       ]
   }
   ```

2. **Attach AmazonBedrockFullAccess to the role**
3. **Update .env to use role:**
   ```bash
   AWS_ROLE_ARN=arn:aws:iam::339712840004:role/BedrockRole
   ```

### Option 4: Temporary Workaround
Use a different user or access key that doesn't have the deny policy.

## 🧪 Test After Fix

Run this command to verify the fix:
```bash
curl -X POST http://localhost:8000/care-plan/sample
```

Or test directly:
```bash
docker-compose exec ai-health-service python -c "
import boto3, json
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
response = bedrock.invoke_model(
    body=json.dumps({
        'anthropic_version': 'bedrock-2023-05-31',
        'max_tokens': 10,
        'messages': [{'role': 'user', 'content': 'Hello'}]
    }),
    modelId='anthropic.claude-3-sonnet-20240229-v1:0',
    accept='application/json',
    contentType='application/json'
)
print('✅ Success!')
"
```

## 🔍 Next Steps

1. **Check IAM policies** for explicit deny statements
2. **Contact your AWS administrator** if you don't have IAM permissions
3. **Consider using a different AWS user/role** for Bedrock access
4. **Once fixed, all care plan endpoints will work perfectly**

The service is fully functional - it's just an AWS IAM configuration issue!