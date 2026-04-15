"""
    Image service functions.

    Provides high-level operations for saving uploaded image files,
    loading them from storage, and updating related database records.
"""


import os
import cv2
import numpy as np
from pathlib import Path
from PIL import Image
from sqlalchemy.orm import Session

from app.config import settings
from app import models, schemas


# ── Quality thresholds ────────────────────────────────────────────────────────
MIN_WIDTH         = 300    # pixels
MIN_HEIGHT        = 300    # pixels
MIN_FILE_SIZE_KB  = 20     # kilobytes  (below this is almost always low quality)
BLUR_THRESHOLD    = 80.0   # Laplacian variance — below this = blurry


def create_upload_dir():
    """Ensure upload directory exists."""
    Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    
    
def check_image_quality(filepath: str) -> tuple[bool, str]:
    """
    Validate image quality before saving to the database.

    Checks:
      1. Minimum file size (rejects near-empty / corrupt files)
      2. Minimum resolution (rejects thumbnails / tiny images)
      3. Blurriness via Laplacian variance (rejects out-of-focus images)

    Returns:
        (True, "")            if the image passes all checks
        (False, reason_str)   if the image fails, with a human-readable reason
    """

    # 1. File size check
    file_size_kb = os.path.getsize(filepath) / 1024
    if file_size_kb < MIN_FILE_SIZE_KB:
        return False, (
            f"Image file is too small ({file_size_kb:.1f} KB). "
            f"Please upload a higher quality image (minimum {MIN_FILE_SIZE_KB} KB)."
        )

    # 2. Resolution check
    try:
        with Image.open(filepath) as img:
            width, height = img.size
    except Exception:
        return False, "Could not read image dimensions. Please upload a valid image file."

    if width < MIN_WIDTH or height < MIN_HEIGHT:
        return False, (
            f"Image resolution is too low ({width}×{height}px). "
            f"Please upload an image of at least {MIN_WIDTH}×{MIN_HEIGHT}px."
        )

    # 3. Blurriness check (Laplacian variance)
    try:
        img_cv = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)
        if img_cv is None:
            return False, "Could not process image for quality check. Please upload a valid image file."

        variance = cv2.Laplacian(img_cv, cv2.CV_64F).var()

        if variance < BLUR_THRESHOLD:
            return False, (
                f"Image appears blurry (sharpness score: {variance:.1f}). "
                "Please upload a sharper, well-focused photo for better object detection."
            )
    except Exception:
        # If OpenCV fails for any reason, allow the image through
        # rather than blocking valid uploads
        pass

    return True, ""


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