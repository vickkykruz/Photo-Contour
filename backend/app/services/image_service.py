"""
    Image service functions.

    Provides high-level operations for saving uploaded image files,
    loading them from storage, and updating related database records.
"""


import os
import shutil
from pathlib import Path
from PIL import Image
from sqlalchemy.orm import Session

from app.config import settings
from app import models, schemas


def create_upload_dir():
    """Ensure upload directory exists."""
    Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)


def save_uploaded_image(db: Session, file_path: str, filename: str) -> models.Image:
    """
    Save uploaded image to filesystem and database.
    
    Returns the created Image record.
    """
    create_upload_dir()
    
    # Get image dimensions
    width, height = 0, 0
    try:
        with Image.open(file_path) as img:
            width, height = img.size
    except:
        pass  # Non-image files get 0x0
    
    # Create DB record
    db_image = models.Image(
        filename=filename,
        filepath=file_path,
        width=width,
        height=height
    )
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    
    return db_image


def get_image_by_id(db: Session, image_id: int) -> models.Image:
    """Get image by ID."""
    return db.query(models.Image).filter(models.Image.id == image_id).first()