"""
    Image service functions.

    Provides high-level operations for saving uploaded image files,
    loading them from storage, and updating related database records.
"""


import os
import uuid
import tempfile
import cv2
from pathlib import Path
from PIL import Image
from app.core.firebase import db, bucket


# ── Quality thresholds ────────────────────────────────────────────────────
MIN_WIDTH        = 300
MIN_HEIGHT       = 300
MIN_FILE_SIZE_KB = 20
BLUR_THRESHOLD   = 80.0


def check_image_quality(filepath: str) -> tuple[bool, str]:
    """Validate image quality before saving."""

    # 1. File size
    file_size_kb = os.path.getsize(filepath) / 1024
    if file_size_kb < MIN_FILE_SIZE_KB:
        return False, (
            f"Image too small ({file_size_kb:.1f} KB). "
            f"Minimum is {MIN_FILE_SIZE_KB} KB."
        )

    # 2. Resolution
    try:
        with Image.open(filepath) as img:
            width, height = img.size
    except Exception:
        return False, "Could not read image. Please upload a valid file."

    if width < MIN_WIDTH or height < MIN_HEIGHT:
        return False, (
            f"Resolution too low ({width}×{height}px). "
            f"Minimum is {MIN_WIDTH}×{MIN_HEIGHT}px."
        )

    # 3. Blurriness
    try:
        img_cv = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)
        if img_cv is not None:
            variance = cv2.Laplacian(img_cv, cv2.CV_64F).var()
            if variance < BLUR_THRESHOLD:
                return False, (
                    f"Image appears blurry (score: {variance:.1f}). "
                    "Please upload a sharper photo."
                )
    except Exception:
        pass

    return True, ""


def save_uploaded_image(
    uid:       str,
    filepath:  str,
    filename:  str,
) -> dict:
    """
    Upload image to Firebase Storage and save metadata to Firestore.
    Returns the image document as a dict.
    """

    # Get dimensions
    width, height = 0, 0
    try:
        with Image.open(filepath) as img:
            width, height = img.size
    except Exception:
        pass

    # Upload to Firebase Storage
    unique_name   = f"{uid}/{uuid.uuid4()}_{filename}"
    blob          = bucket.blob(unique_name)
    blob.upload_from_filename(filepath)
    blob.make_public()
    public_url    = blob.public_url

    # Save metadata to Firestore
    doc_ref = db.collection("images").document()
    data    = {
        "id":         doc_ref.id,
        "uid":        uid,
        "filename":   filename,
        "filepath":   unique_name,   # Storage path
        "url":        public_url,    # Public download URL
        "width":      width,
        "height":     height,
        "created_at": firestore.SERVER_TIMESTAMP,
    }
    doc_ref.set(data)

    return {**data, "created_at": None}


def get_image_by_id(image_id: str, uid: str) -> dict | None:
    """Get image metadata from Firestore by document ID."""
    doc = db.collection("images").document(image_id).get()
    if not doc.exists:
        return None
    data = doc.to_dict()
    # Ensure user owns this image
    if data.get("uid") != uid:
        return None
    return data


def list_images(uid: str) -> list[dict]:
    """List all images belonging to the current user."""
    docs = (
        db.collection("images")
        .where("uid", "==", uid)
        .order_by("created_at", direction="DESCENDING")
        .stream()
    )
    results = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        results.append(data)
    return results