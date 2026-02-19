"""
    Object detection service.

    Wraps the computer vision model (e.g. Detectron2) used to
    automatically detect objects in an uploaded image and return
    their coordinates and labels for use in the studio UI.
"""


import cv2
import numpy as np
from ultralytics import YOLO
from typing import List, Dict
from pathlib import Path
from sqlalchemy.orm import Session

from app.models import Image
from app.schemas.hotspots import BBox, DetectedObject, DetectionResult


# Load YOLOv8 model ONCE at module import (singleton pattern)
_model = YOLO("yolov8n-seg.pt")  # nano segmentation model (fast)
_model.to("cpu")


# Basic Object detection
COCO_CLASSES = [
    "person", "bicycle", "car", "motorcycle", "airplane", "bus", "train", "truck", 
    "boat", "traffic light", "fire hydrant", "stop sign", "parking meter", "bench",
    "bird", "cat", "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra",
    "giraffe", "backpack", "umbrella", "handbag", "tie", "suitcase", "frisbee",
    "skis", "snowboard", "sports ball", "kite", "baseball bat", "baseball glove",
    "skateboard", "surfboard", "tennis racket", "bottle", "wine glass", "cup",
    "fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange",
    "broccoli", "carrot", "hot dog", "pizza", "donut", "cake", "chair", "couch",
    "potted plant", "bed", "dining table", "toilet", "tv", "laptop", "mouse",
    "remote", "keyboard", "cell phone", "microwave", "oven", "toaster", "sink",
    "refrigerator", "book", "clock", "vase", "scissors", "teddy bear", "hair drier",
    "toothbrush"
]


def run_yolo_detection(db: Session, image_id: int) -> DetectionResult:
    """Run REAL YOLOv8 detection on the image."""
    image = db.query(Image).filter(Image.id == image_id).first()
    if image is None:
        raise ValueError("Image not found")
    
    if not image.filepath or not Path(image.filepath).exists():
        raise ValueError("Image file not found")
    
    # Run YOLOv8 inference
    results = _model(
        image.filepath,
        verbose=False,
        device='cpu',
        imgsz=640,
        conf=0.25,
        retina_masks=True)[0]
    
    objects = []
    img_h, img_w = results.orig_shape

    for i, r in enumerate(results):
        if r.masks is not None:
            # Get contour points directly from mask (hugs object shape)
            contour = r.masks.xy[0].astype(np.int32)  # [[x1,y1], [x2,y2], ...]
            
            # Convert to normalized SVG coordinates (0-1 scale)
            contour_svg = [(pt[0]/img_w, pt[1]/img_h) for pt in contour]
            
            objects.append({
                "id": i,
                "label": _model.names[int(r.boxes.cls[0])],
                "score": float(r.boxes.conf[0]),
                "contour": contour_svg,  # Exact object outline points
                "bbox": {  # Fallback rectangle for reference
                    "x1": float(r.boxes.xyxy[0][0]/img_w),
                    "y1": float(r.boxes.xyxy[0][1]/img_w),
                    "x2": float(r.boxes.xyxy[0][2]/img_w),
                    "y2": float(r.boxes.xyxy[0][3]/img_w),
                }
            })

    
    return {"image_id": image_id, "width": img_w, "height": img_h, "objects": objects}


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