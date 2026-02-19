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


router = APIRouter(prefix="/hotspots", tags=["hotspots"])


@router.post("/detect/{image_id}", response_model=DetectionResult)
def detect_objects(image_id: int, db: Session = Depends(get_db)):
    """
    Run REAL YOLOv8 object detection on the given image.

    Returns a single bounding box in the center of the image.
    """
    try:
        result = detection_service.run_yolo_detection(db, image_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")
    
    
@router.post("/generate-svg", response_model=SvgResponse)
def generate_svg(hotspot: HotspotCreate, db: Session = Depends(get_db)):
    """
    Generate a simple SVG that highlights the selected object
    and attaches the provided text and link.
    """
    # Run fake detection again to get boxes
    try:
        detection = detection_service.run_fake_detection(db, hotspot.image_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    try:
        svg = svg_service.generate_simple_svg(db, detection, hotspot)
        return svg
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))