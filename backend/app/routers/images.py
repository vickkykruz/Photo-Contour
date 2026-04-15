"""
    Image management API endpoints.

    Implements routes for uploading images, fetching image metadata,
    and serving original image files to the frontend studio.
"""


import os
import shutil
import tempfile
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import RedirectResponse
from typing import List

from app.core.deps import get_current_user
from app.config import settings
from app.services.image_service import (
    check_image_quality,
    save_uploaded_image,
    get_image_by_id,
    list_images,
)


router = APIRouter(prefix="/images", tags=["images"])


@router.post("/")
async def upload_image(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    """Upload image to Firebase Storage after quality validation."""

    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image.")

    # Save temporarily for quality check and YOLO processing
    suffix   = os.path.splitext(file.filename)[1]
    tmp_path = os.path.join(settings.UPLOAD_DIR, f"tmp_{file.filename}")

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    with open(tmp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Quality check
    passed, reason = check_image_quality(tmp_path)
    if not passed:
        os.remove(tmp_path)
        raise HTTPException(status_code=422, detail=reason)

    # Upload to Firebase Storage
    try:
        image = save_uploaded_image(
            uid=current_user["uid"],
            filepath=tmp_path,
            filename=file.filename,
        )
    finally:
        # Always clean up temp file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    return image


@router.get("/")
def list_user_images(
    current_user: dict = Depends(get_current_user),
):
    """List all images for the current user."""
    return list_images(uid=current_user["uid"])


@router.get("/{image_id}")
def get_image(
    image_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Get image metadata by ID."""
    image = get_image_by_id(image_id, uid=current_user["uid"])
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    return image


@router.get("/{image_id}/file")
def get_image_file(
    image_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Redirect to the Firebase Storage public URL for this image.
    The frontend img tag follows the redirect automatically.
    """
    image = get_image_by_id(image_id, uid=current_user["uid"])
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    return RedirectResponse(url=image["url"])