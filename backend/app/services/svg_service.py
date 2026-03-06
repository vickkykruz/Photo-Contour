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



# def _image_to_base64(filepath: str) -> tuple[str, int, int]:
#     """Convert image file to data URI + dimensions."""
#     with open(filepath, "rb") as f:
#         data = base64.b64encode(f.read()).decode()
    
#     with PilImage.open(filepath) as img:
#         w, h = img.size
    
#     mime = f"image/{Path(filepath).suffix.lstrip('.')}"
#     return f"data:{mime};base64,{data}", w, h


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
    
    print("Image size:", w, h)
    print("First 5 contour points (raw):", contour_points[:5])
    print("First 5 contour points (scaled):", scaled_points[:5])
    
    # ✅ FIXED: User-controlled styling (not system colors)
    # User picks color via frontend or defaults to professional blue
    stroke_color = hotspot.color or "#3b82f6"  # Blue (tailwind-blue-500)
    
    # Embed image
    with open(image.filepath, "rb") as f:
        img_data = base64.b64encode(f.read()).decode()
        
    # ── Popup card positioning ────────────────────────────────────────────────
    # Use the object's bounding box (normalized) to place the popup nearby
    bbox_x1 = obj.bbox.x1 * w
    bbox_y1 = obj.bbox.y1 * h
    bbox_x2 = obj.bbox.x2 * w
    bbox_y2 = obj.bbox.y2 * h
    bbox_cx = (bbox_x1 + bbox_x2) / 2

    popup_w = min(200, w * 0.85)
    popup_h = 96

    # Horizontally center on the object; clamp inside image bounds
    popup_x = max(4, min(bbox_cx - popup_w / 2, w - popup_w - 4))

    # Prefer placing popup above the object; fall back to below
    if bbox_y1 > popup_h + 20:
        popup_y = bbox_y1 - popup_h - 12
    else:
        popup_y = bbox_y2 + 12

    # Final clamp so card never leaves the image
    popup_y = max(4, min(popup_y, h - popup_h - 4))

    # ── Text truncation (SVG has no native wrapping) ─────────────────────────
    line1 = hotspot.text[:38]
    line2 = hotspot.text[38:76] if len(hotspot.text) > 38 else ""
    line2_svg = (
        f'<text x="{popup_x + 10:.1f}" y="{popup_y + 58:.1f}" '
        f'font-family="Arial, sans-serif" font-size="11" fill="#374151">{line2}</text>'
        if line2 else ""
    )
    
    # ── SVG ──────────────────────────────────────────────────────────────────
    svg = f"""<?xml version="1.0" encoding="UTF-8"?>
    <svg xmlns="http://www.w3.org/2000/svg"
        xmlns:xlink="http://www.w3.org/1999/xlink"
        viewBox="0 0 {w} {h}"
        style="width:100%;height:auto;display:block;max-height:100vh;">

    <style>
        .hotspot-path  {{ cursor: pointer; }}
        .hotspot-path:hover {{ fill: rgba(59,130,246,0.35); }}
        .popup         {{ visibility: hidden; opacity: 0; transition: opacity 0.18s; pointer-events: none; }}
        .hotspot-group:hover .popup {{ visibility: visible; opacity: 1; pointer-events: all; }}
        .visit-btn rect {{ transition: fill 0.15s; }}
        .visit-btn:hover rect {{ fill: #1d4ed8; }}
    </style>

    <!-- Original image -->
    <image href="data:image/jpeg;base64,{img_data}"
            x="0" y="0" width="{w}" height="{h}"
            preserveAspectRatio="xMidYMid meet"/>

    <!-- Interactive group: contour + popup card -->
    <g class="hotspot-group">

        <!-- Object contour path -->
        <path class="hotspot-path"
            d="{path_data}"
            fill="rgba(59,130,246,0.18)"
            stroke="{stroke_color}"
            stroke-width="2.5"
            stroke-linejoin="round"
            stroke-linecap="round">
        <animate attributeName="stroke-opacity"
                values="0.5;1;0.5" dur="2.5s" repeatCount="indefinite"/>
        </path>

        <!-- Popup card (shown on hover) -->
        <g class="popup">

        <!-- Drop shadow -->
        <rect x="{popup_x + 3:.1f}" y="{popup_y + 3:.1f}"
                width="{popup_w:.1f}" height="{popup_h:.1f}"
                rx="8" ry="8" fill="rgba(0,0,0,0.18)"/>

        <!-- Card body -->
        <rect x="{popup_x:.1f}" y="{popup_y:.1f}"
                width="{popup_w:.1f}" height="{popup_h:.1f}"
                rx="8" ry="8" fill="white" stroke="#e2e8f0" stroke-width="1"/>

        <!-- Coloured header band -->
        <rect x="{popup_x:.1f}" y="{popup_y:.1f}"
                width="{popup_w:.1f}" height="26"
                rx="8" ry="8" fill="{stroke_color}"/>
        <!-- Square off the bottom corners of the header -->
        <rect x="{popup_x:.1f}" y="{popup_y + 18:.1f}"
                width="{popup_w:.1f}" height="8" fill="{stroke_color}"/>

        <!-- Object label in header -->
        <text x="{popup_x + popup_w / 2:.1f}" y="{popup_y + 17:.1f}"
                text-anchor="middle"
                font-family="Arial, sans-serif" font-size="11"
                font-weight="bold" fill="white">{obj.label.upper()}</text>

        <!-- User description (up to 2 lines) -->
        <text x="{popup_x + 10:.1f}" y="{popup_y + 44:.1f}"
                font-family="Arial, sans-serif" font-size="11"
                fill="#374151">{line1}</text>
        {line2_svg}

        <!-- Visit link button -->
        <a href="{hotspot.link}" target="_blank">
            <g class="visit-btn">
            <rect x="{popup_x + popup_w / 2 - 46:.1f}" y="{popup_y + popup_h - 24:.1f}"
                    width="92" height="20" rx="4" ry="4" fill="{stroke_color}"/>
            <text x="{popup_x + popup_w / 2:.1f}" y="{popup_y + popup_h - 10:.1f}"
                    text-anchor="middle"
                    font-family="Arial, sans-serif" font-size="10"
                    font-weight="bold" fill="white">Visit Link →</text>
            </g>
        </a>

        </g>
    </g>

    </svg>"""

    return SvgResponse(image_id=image.id, svg=svg, preview_url=f"/images/{image.id}/file")