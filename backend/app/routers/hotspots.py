"""
    Hotspot and object-detection API endpoints.

    Defines routes to run object detection on an uploaded image,
    create or update hotspots for a selected object, and generate
    the final interactive SVG file for download.
"""


from fastapi import APIRouter, Depends, HTTPException, Response
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
    return result
    
    
@router.post("/generate-svg", response_model=SvgResponse)
def generate_svg(hotspot: HotspotCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Generate a simple SVG that highlights the selected object
    and attaches the provided text and link.
    """
    return svg_service.generate_interactive_svg(db, hotspot)


@router.get("/{image_id}/{object_id}/download-svg", response_class=Response)
def download_svg(
    image_id: int,
    object_id: int,
    text: str = "object",
    link: str = "https://example.com",
    db: Session = Depends(get_db)
):
    hotspot = HotspotCreate(
        image_id=image_id,
        object_id=object_id,
        text=text,
        link=link,
    )

    result = svg_service.generate_interactive_svg(db, hotspot)

    return Response(
        content=result.svg,
        media_type="image/svg+xml",
        headers={
            "Content-Disposition": (
                f'attachment; filename="image_{image_id}_obj_{object_id}_{text}.svg"'
            ),
        },
    )