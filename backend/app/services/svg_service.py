"""
    SVG generation service.

    Builds interactive SVG documents that embed the original image as a
    background layer and overlay the selected hotspot region along with
    hover/click annotations containing user-provided text and links.
"""


from pathlib import Path
from sqlalchemy.orm import Session

from app.models import Image
from app.schemas.hotspots import DetectionResult, HotspotCreate, SvgResponse


def generate_simple_svg(
    db: Session,
    detection: DetectionResult,
    hotspot: HotspotCreate,
) -> SvgResponse:
    """
    Generate a minimal SVG string for the given hotspot.

    Draws a rectangle for the selected object and includes the
    annotation text as a <title> for hover tooltips.
    """
    image: Image | None = db.query(Image).filter(Image.id == hotspot.image_id).first()
    if image is None:
        raise ValueError("Image not found")

    # Find selected object
    obj = next((o for o in detection.objects if o.id == hotspot.object_id), None)
    if obj is None:
        raise ValueError("Selected object not found in detection result")

    # Use relative path in SVG (frontends can adapt later)
    image_path = Path(image.filepath).as_posix()

    svg = f"""
<svg xmlns="http://www.w3.org/2000/svg" width="{image.width or 800}" height="{image.height or 600}">
  <image href="{image_path}" x="0" y="0" width="{image.width or 800}" height="{image.height or 600}" />
  <a href="{hotspot.link}">
    <rect x="{obj.bbox.x}" y="{obj.bbox.y}"
          width="{obj.bbox.width}" height="{obj.bbox.height}"
          fill="none" stroke="gold" stroke-width="4">
      <title>{hotspot.text}</title>
    </rect>
  </a>
</svg>
""".strip()

    return SvgResponse(image_id=hotspot.image_id, svg=svg)