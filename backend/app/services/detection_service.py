"""
    Object detection service.

    Wraps the computer vision model (e.g. Detectron2) used to
    automatically detect objects in an uploaded image and return
    their coordinates and labels for use in the studio UI.
"""


from sqlalchemy.orm import Session
from app.models import Image
from app.schemas.hotspots import BBox, DetectedObject, DetectionResult


def run_fake_detection(db: Session, image_id: int) -> DetectionResult:
    """
    Return a fake detection result for the given image.

    Uses the stored image dimensions to create a bounding box
    in the center of the image.
    """
    image: Image | None = db.query(Image).filter(Image.id == image_id).first()
    if image is None:
        raise ValueError("Image not found")

    # Fallback dimensions if not set
    width = image.width or 400
    height = image.height or 400

    # Simple central box (50% of width/height)
    box_w = int(width * 0.5)
    box_h = int(height * 0.5)
    x = int((width - box_w) / 2)
    y = int((height - box_h) / 2)

    bbox = BBox(x=x, y=y, width=box_w, height=box_h)
    detected = DetectedObject(
        id=0,
        label="object",   # later: 'poster', etc.
        score=0.9,
        bbox=bbox,
    )

    return DetectionResult(image_id=image_id, objects=[detected])