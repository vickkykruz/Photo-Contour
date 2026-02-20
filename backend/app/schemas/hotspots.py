"""
    Pydantic models for detected objects and interactive hotspots.

    Provides schemas for object detection results, hotspot creation
    (user text + link bound to a detected region), and SVG generation
    responses.
"""


from pydantic import BaseModel
from typing import List, Optional


class Point(BaseModel):
    """Align point in the image"""
    x: float
    y: float


class BBox(BaseModel):
    """Axis-aligned bounding box in image coordinates."""
    x1: float
    y1: float
    x2: float
    y2: float
    
    
class DetectedObject(BaseModel):
    """Single detected object returned by detection service."""
    id: int              # simple index
    label: str           # e.g. 'poster'
    score: float         # confidence (stubbed)
    contour: Optional[List[List[float]]] = None  # [[x1,y1], [x2,y2], ...] normalized 0-1
    bbox: BBox
    
    
class DetectionResult(BaseModel):
    """List of detected objects for an image."""
    image_id: int
    width: Optional[float] = None
    height: Optional[float] = None
    objects: List[DetectedObject]
    
    
class HotspotCreate(BaseModel):
    """Data needed to create a hotspot and generate SVG."""
    image_id: int
    object_id: int       # index of selected detected object
    text: str
    link: str
    color: Optional[str] = "#3b82f6"
    
    
class SvgResponse(BaseModel):
    """Generated SVG document as a string."""
    image_id: int
    svg: str
    preview_url: str