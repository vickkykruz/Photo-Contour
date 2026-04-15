"""
    Hotspot and object-detection API endpoints.

    Defines routes to run object detection on an uploaded image,
    create or update hotspots for a selected object, and generate
    the final interactive SVG file for download.
"""


from fastapi import APIRouter, Depends, HTTPException, Response
from app.schemas.hotspots import DetectionResult, HotspotCreate, SvgResponse
from app.services.detection_service import run_yolo_detection
from app.services.svg_service import generate_interactive_svg
from app.core.deps import get_current_user
from app.core.firebase import db


router = APIRouter(prefix="/hotspots", tags=["hotspots"])


@router.post("/detect/{image_id}", response_model=DetectionResult)
def detect_objects(
    image_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Run YOLOv8 segmentation on the given image."""

    # Load image from Firestore
    doc = db.collection("images").document(image_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Image not found")

    image_dict = doc.to_dict()
    image_dict["id"] = doc.id

    # Ensure user owns this image
    if image_dict.get("uid") != current_user.get("uid"):
        raise HTTPException(status_code=403, detail="Access denied")

    return run_yolo_detection(image_dict)


@router.post("/generate-svg", response_model=SvgResponse)
def generate_svg(
    hotspot: HotspotCreate,
    current_user: dict = Depends(get_current_user),
):
    """Generate interactive SVG for the selected object."""
    return generate_interactive_svg(hotspot, current_user)


@router.get("/{image_id}/{object_id}/download-svg",
            response_class=Response)
def download_svg(
    image_id:  str,
    object_id: int,
    text:      str = "object",
    link:      str = "https://example.com",
    current_user: dict = Depends(get_current_user),
):
    """Download the generated SVG file."""
    hotspot = HotspotCreate(
        image_id=image_id,
        object_id=object_id,
        text=text,
        link=link,
    )
    result = generate_interactive_svg(hotspot, current_user)
    return Response(
        content=result.svg,
        media_type="image/svg+xml",
        headers={
            "Content-Disposition": (
                f'attachment; filename="photo_contour_{image_id}_{object_id}.svg"'
            ),
        },
    )