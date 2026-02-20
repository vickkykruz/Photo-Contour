"""
    Hotspot and object-detection API endpoints.

    Defines routes to run object detection on an uploaded image,
    create or update hotspots for a selected object, and generate
    the final interactive SVG file for download.
"""


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.schemas.hotspots import DetectionResult, HotspotCreate, SvgResponse
from app.services import detection_service, svg_service
from app.core.deps import get_current_user
from app.models import User


router = APIRouter(prefix="/hotspots", tags=["hotspots"])


@router.post("/detect/{image_id}", response_model=DetectionResult)
def detect_objects(image_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Run YOLOv8 SEGMENTATION on the given image.

    Returns object contours (not rectangles).
    """
    result = detection_service.run_yolo_detection(db, image_id)
    return DetectionResult(**result)
    
    
@router.post("/generate-svg", response_model=SvgResponse)
def generate_svg(hotspot: HotspotCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Generate a simple SVG that highlights the selected object
    and attaches the provided text and link.
    """
    return svg_service.generate_interactive_svg(db, hotspot)