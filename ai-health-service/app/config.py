from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # AWS Configuration
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_region: str = "us-east-1"
    aws_role_arn: Optional[str] = None  # For role-based access
    
    # S3 Configuration
    s3_bucket_name: str
    
    # Amazon Bedrock Configuration
    bedrock_model_id: str = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
    bedrock_region: Optional[str] = None  # Uses aws_region if not specified
    
    # Application Configuration
    app_name: str = "AI Health Service"
    app_version: str = "1.0.0"
    debug: bool = True
    
    @property
    def effective_bedrock_region(self) -> str:
        """Get the effective Bedrock region (bedrock_region or aws_region)"""
        return self.bedrock_region or self.aws_region
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()