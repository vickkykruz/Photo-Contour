"""
    Object detection service.

    Wraps the computer vision model (e.g. Detectron2) used to
    automatically detect objects in an uploaded image and return
    their coordinates and labels for use in the studio UI.
"""


import requests
from pathlib import Path
from sqlalchemy.orm import Session

from app.models import Image
from app.schemas.hotspots import BBox, DetectedObject, DetectionResult


YOLO_SERVICE_URL = "http://localhost:8002/detect"

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
    payload = {"image_path": image.filepath}
    try:
        resp = requests.post(YOLO_SERVICE_URL, json=payload, timeout=30)
    except requests.RequestException as e:
        raise RuntimeError(f"YOLO service unreachable: {e}")

    if resp.status_code != 200:
        raise RuntimeError(f"YOLO service error: {resp.status_code} {resp.text}")
    
    data = resp.json()

    objects = [
        DetectedObject(
            id=o["id"],
            label=o["label"],
            score=o["score"],
            bbox=BBox(**o["bbox"])
        )
        for o in data["objects"]
    ]

    return DetectionResult(image_id=image_id, objects=objects)