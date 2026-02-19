"""
    SVG generation service.

    Builds interactive SVG documents that embed the original image as a
    background layer and overlay the selected hotspot region along with
    hover/click annotations containing user-provided text and links.
"""


import cv2
import base64
from pathlib import Path
from PIL import Image as PilImage
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models import Image
from app.schemas.hotspots import DetectionResult, HotspotCreate, SvgResponse, BBox
from app.services import detection_service



def _image_to_base64(filepath: str) -> tuple[str, int, int]:
    """Convert image file to data URI + dimensions."""
    with open(filepath, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    
    with PilImage.open(filepath) as img:
        w, h = img.size
    
    mime = f"image/{Path(filepath).suffix.lstrip('.')}"
    return f"data:{mime};base64,{data}", w, h


def generate_interactive_svg(
    db: Session,
    hotspot: HotspotCreate,
) -> SvgResponse:
    image = db.query(Image).filter(Image.id == hotspot.image_id).first()
    detection_result = detection_service.run_yolo_segmentation(db, hotspot.image_id)
    
    obj = next((o for o in detection_result["objects"] if o["id"] == hotspot.object_id), None)
    if not image or not obj:
        raise HTTPException(status_code=404, detail="Image or object not found")
    
    # 2. Embed original image as base64
    with open(image.filepath, "rb") as f:
        img_data = base64.b64encode(f.read()).decode()
    
    w, h = detection_result["width"], detection_result["height"]
    
    # 3. Convert contour points to SVG path
    contour_points = obj["contour"]  # List of (x,y) normalized 0-1
    path_data = "M " + " ".join([f"{x},{y}" for x,y in contour_points]) + " Z"    
    
    # 4. Build complete SVG
    svg = f"""<?xml version="1.0" encoding="UTF-8"?>
    <svg xmlns="http://www.w3.org/2000/svg" 
        xmlns:xlink="http://www.w3.org/1999/xlink"
        width="{w}" height="{h}" viewBox="0 0 {w} {h}">
    
    <!-- Original image (visually identical) -->
    <image href="data:image/jpeg;base64,{img_data}" x="0" y="0" width="{w}" height="{h}" preserveAspectRatio="xMidYMid slice"/>
    
    <!-- Clickable contour border hugging the object -->
    <a href="{hotspot.link}" target="_blank">
        <path d="{path_data}"
            fill="none"
            stroke="#ff4444"
            stroke-width="3"
            stroke-linejoin="round"
            stroke-linecap="round">
        <title>{hotspot.text}</title>
        </path>
    </a>
    
    </svg>"""

    return SvgResponse(svg=svg, preview_url=f"/images/{image.id}/file")