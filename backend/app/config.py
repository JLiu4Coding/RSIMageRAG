"""Configuration management for the application."""
import os
from pathlib import Path
from typing import Optional

try:
    from pydantic_settings import BaseSettings
except ImportError:
    # Fallback for older pydantic versions
    from pydantic import BaseSettings


# Find the backend directory (where .env file should be)
BACKEND_DIR = Path(__file__).parent.parent
ENV_FILE = BACKEND_DIR / ".env"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    openai_api_key: str
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_default_region: str = "us-west-1"
    aws_s3_bucket: str
    langchain_tracing_v2: str = "true"
    langchain_endpoint: Optional[str] = None
    langchain_api_key: Optional[str] = None
    
    # Model settings
    vision_model: str = "gpt-4o"
    embedding_model: str = "text-embedding-3-small"
    
    # Paths
    upload_dir: str = "uploads"
    jpeg_dir: str = "images_jpeg"
    vectorstore_dir: str = "vectorstore"
    
    class Config:
        env_file = str(ENV_FILE)
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()

