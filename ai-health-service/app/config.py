from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # AWS Configuration
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_region: str = "us-east-1"
    
    # S3 Configuration
    s3_bucket_name: str
    
    # Application Configuration
    app_name: str = "AI Health Service"
    app_version: str = "1.0.0"
    debug: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()