"""
    Object detection service.

    Wraps the computer vision model (e.g. Detectron2) used to
    automatically detect objects in an uploaded image and return
    their coordinates and labels for use in the studio UI.
"""


from typing import List
import cv2
from ultralytics import YOLO
from sqlalchemy.orm import Session
from pathlib import Path

from app.models import Image
from app.schemas.hotspots import BBox, DetectedObject, DetectionResult


# Load YOLOv8 model ONCE at module import (singleton pattern)
_model = YOLO("yolov8n.pt")  # nano model, fast + good enough


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
    results = _model(image.filepath, verbose=False)
    
    objects = []
    for r in results:
        boxes = r.boxes
        if boxes is not None:
            for box in boxes:
                # Extract bbox, confidence, class
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                conf = box.conf[0].cpu().numpy()
                cls_id = int(box.cls[0].cpu().numpy())
                
                # Filter low confidence (< 0.5)
                if conf < 0.5:
                    continue
                
                label = COCO_CLASSES[cls_id]
                w = x2 - x1
                h = y2 - y1
                
                detected = DetectedObject(
                    id=len(objects),
                    label=label,
                    score=float(conf),
                    bbox=BBox(
                        x1=float(x1), y1=float(y1),
                        x2=float(x2), y2=float(y2),
                        width=float(w), height=float(h)
                    )
                )
                objects.append(detected)
    
    return DetectionResult(image_id=image_id, objects=objects)


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