"""
    Configuration and environment settings for the backend.

    Defines strongly-typed settings (database URL, JWT secrets, storage paths,
    CORS origins, etc.) using Pydantic and loads them from environment variables
    or default values for development.
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):

    # ── Project ───────────────────────────────────────────────────────────
    PROJECT_NAME: str = "Photo Contour API"
    VERSION:      str = "0.1.0"

    # ── CORS ─────────────────────────────────────────────────────────────
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "https://vickkykruzprogramming.dev",
    ]

    # ── Firebase ──────────────────────────────────────────────────────────
    FIREBASE_CREDENTIALS_PATH: str = "./firebase-credentials.json"
    FIREBASE_STORAGE_BUCKET:   str = ""  # e.g. photo-contour-xxxxx.appspot.com

    # ── Upload (temp dir for YOLO processing) ────────────────────────────
    UPLOAD_DIR: str = "./static/uploads"

    class Config:
        env_file = ".env"


settings = Settings()