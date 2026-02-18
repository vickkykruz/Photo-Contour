"""
    Image management API endpoints.

    Implements routes for uploading images, fetching image metadata,
    and serving original image files to the frontend studio.
"""


import os
import shutil
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List

from app import schemas, services
from app.db.base import get_db
from app.models import Image
from app.config import settings
from app.core.deps import get_current_user
from app.models import User


router = APIRouter(prefix="/images", tags=["images"])


@router.post("/", response_model=schemas.ImageResponse)
async def upload_image(
    file: UploadFile = File(..., description="Image file to upload"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a new image.
    
    Saves file to static/uploads/ and creates database record.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(400, "File must be an image")
    
    # Generate unique filename
    filename = f"{file.filename}"
    filepath = os.path.join(settings.UPLOAD_DIR, filename)
    
    # Save file
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Create DB record
    image = services.save_uploaded_image(db, filepath, filename)
    
    return image


@router.get("/{image_id}", response_model=schemas.ImageResponse)
def get_image(image_id: int, db: Session = Depends(get_db)):
    """Get image metadata by ID."""
    image = services.get_image_by_id(db, image_id)
    if not image:
        raise HTTPException(404, "Image not found")
    return image


@router.get("/", response_model=List[schemas.ImageResponse])
def list_images(db: Session = Depends(get_db)):
    """List all images (no auth yet)."""
    images = db.query(Image).all()
    return images


@router.get("/{image_id}/file")
def get_image_file(image_id: int, db: Session = Depends(get_db)):
    """
    Return the raw image file for a given image ID.

    This will be used by the studio frontend to display
    the original image in the browser.
    """
    image = services.get_image_by_id(db, image_id)
    if not image:
        raise HTTPException(404, "Image not found")
    
    if not os.path.exists(image.filepath):
        raise HTTPException(404, "Image file not found on disk")
    
    return FileResponse(image.filepath, media_type="image/*", filename=image.filename)