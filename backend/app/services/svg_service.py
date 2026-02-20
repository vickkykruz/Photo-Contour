"""
    SVG generation service.

    Builds interactive SVG documents that embed the original image as a
    background layer and overlay the selected hotspot region along with
    hover/click annotations containing user-provided text and links.
"""


import base64
from pathlib import Path
from PIL import Image as PilImage
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models import Image
from app.schemas.hotspots import HotspotCreate, SvgResponse
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
    detection_result = detection_service.run_yolo_detection(db, hotspot.image_id)
    
    obj = next((o for o in detection_result.objects if o.id == hotspot.object_id), None)
    if not image or not obj:
        raise HTTPException(status_code=404, detail="Image or object not found")
    
    w, h = detection_result.width, detection_result.height
    contour_points = obj.contour
    scaled_points = [(x * w, y * h) for x, y in contour_points]
    path_data = "M " + " ".join([f"{x:.1f},{y:.1f}" for x, y in scaled_points]) + " Z"
    
    # ✅ FIXED: User-controlled styling (not system colors)
    # User picks color via frontend or defaults to professional blue
    stroke_color = hotspot.color or "#3b82f6"  # Blue (tailwind-blue-500)
    
    # Embed image
    with open(image.filepath, "rb") as f:
        img_data = base64.b64encode(f.read()).decode()    
    
    # ✅ Production SVG - USER annotation focused
    svg = f"""<?xml version="1.0" encoding="UTF-8"?>
    <svg xmlns="http://www.w3.org/2000/svg" 
        xmlns:xlink="http://www.w3.org/1999/xlink"
        width="{w}" height="{h}" viewBox="0 0 {w} {h}">
    
    <!-- User's uploaded image -->
    <image href="data:image/jpeg;base64,{img_data}" x="0" y="0" width="{w}" height="{h}"/>
    
    <!-- USER'S annotation (clickable) -->
    <a href="{hotspot.link}" target="_blank">
        <path d="{path_data}"
            fill="rgba(59,130,246,0.2)"
            stroke="{stroke_color}"
            stroke-width="4"
            stroke-linejoin="round"
            stroke-linecap="round">
        <title>{hotspot.text} - Click to visit</title>
        <animate attributeName="opacity" values="0.8;1;0.8" dur="3s" repeatCount="indefinite"/>
        </path>
    </a>
    
    <!-- Detection confidence (for user reference) -->
    <text x="10" y="20" font-size="14" fill="#666" font-family="Arial">
        Detected: {obj.label} ({obj.score:.0%})
    </text>
    </svg>"""

    return SvgResponse(image_id=image.id, svg=svg, preview_url=f"/images/{image.id}/file")