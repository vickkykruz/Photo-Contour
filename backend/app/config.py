"""
    Configuration and environment settings for the backend.

    Defines strongly-typed settings (database URL, JWT secrets, storage paths,
    CORS origins, etc.) using Pydantic and loads them from environment variables
    or default values for development.
"""

from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./photo_contour.db"
    
    # Project paths
    UPLOAD_DIR: str = "./static/uploads"
    
    # CORS for frontend
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # Server
    PROJECT_NAME: str = "Photo Contour API"
    VERSION: str = "0.1.0"
    
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    class Config:
        env_file = ".env"

# Global settings instance
settings = Settings()