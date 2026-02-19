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

from app.models import Image
from app.schemas.hotspots import DetectionResult, HotspotCreate, SvgResponse, BBox


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
    detection: DetectionResult,
    hotspot: HotspotCreate,
) -> SvgResponse:
    img = db.query(Image).filter(Image.id == hotspot.image_id).first()
    if not img:
        raise ValueError("Image not found")
    
    obj = next((o for o in detection.objects if o.id == hotspot.object_id), None)
    if not obj:
        raise ValueError("Object not found")
    
    bbox: BBox = obj.bbox
    
    # Center info box above the detection
    info_x = bbox.x1 + (bbox.width / 2) - 110  # 220px wide box
    info_y = max(bbox.y1 - 60, 10)
    
    data_uri, svg_w, svg_h = _image_to_base64(img.filepath)
    
    svg = f'''
    <svg xmlns="http://www.w3.org/2000/svg" width="{svg_w}" height="{svg_h}">
    <style>
        .hotspot-info {{
        opacity: 0;
        transition: opacity 0.3s ease;
        pointer-events: none;
        }}
        .hotspot:hover .hotspot-info {{
        opacity: 1;
        }}
        .hotspot:hover .hotspot-rect {{
        stroke: #FFD700;
        stroke-width: 4;
        fill: rgba(255,215,0,0.1);
        }}
        .hotspot-rect {{
        stroke: rgba(255,215,0,0.5);
        stroke-width: 2;
        fill: none;
        transition: all 0.3s ease;
        }}
    </style>
    
    <image href="{data_uri}" x="0" y="0" width="{svg_w}" height="{svg_h}"/>
    
    <g class="hotspot">
        <rect class="hotspot-rect" 
            x="{bbox.x1}" y="{bbox.y1}" 
            width="{bbox.width}" height="{bbox.height}"/>
        
        <foreignObject x="{info_x}" y="{info_y}" width="220" height="60" class="hotspot-info">
        <body xmlns="http://www.w3.org/1999/xhtml" 
                style="background: rgba(0,0,0,0.85); color: white; 
                    font-family: Arial, sans-serif; font-size: 12px; 
                    padding: 8px; border-radius: 6px; line-height: 1.3;">
            <div>
            <strong>{obj.label}</strong><br/>
            <span style="font-size: 11px;">{hotspot.text}</span><br/>
            <a href="{hotspot.link}" target="_blank" 
                style="color: #FFD700; text-decoration: none; font-size: 11px;">→ View</a>
            </div>
        </body>
        </foreignObject>
    </g>
    </svg>
    '''.strip()
    
    return SvgResponse(image_id=hotspot.image_id, svg=svg)

    
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