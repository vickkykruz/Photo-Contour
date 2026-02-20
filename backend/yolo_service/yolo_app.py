"""
    YOLOv8 Segmentation Microservice - Object Contour Detection

    Exposes FastAPI endpoints that receive an image path, run YOLOv8 
    segmentation, and return BOTH bounding boxes AND pixel-precise 
    object contours for perfect SVG path generation.
"""



from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from ultralytics import YOLO
import numpy as np
import os


app = FastAPI(title="YOLO Segmentation Service - Contour Detection")

# Load model once
_model = YOLO("yolov8n-seg.pt")  # detection model
_model.to("cpu")


class BBox(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float


class DetectedObject(BaseModel):
    id: int
    label: str
    score: float
    bbox: BBox
    contour: List[List[float]]  # [[x1,y1], [x2,y2], ...] - exact object outline
    
    
class DetectRequest(BaseModel):
    image_path: str


class DetectResponse(BaseModel):
    objects: List[DetectedObject]


@app.post("/detect", response_model=DetectResponse)
def detect(req: DetectRequest):
    """Run YOLOv8 segmentation and return object contours."""
    
    if not os.path.exists(req.image_path):
        raise HTTPException(status_code=404, detail="Image not found")

    results = _model(
        source=req.image_path,
        device="cpu",
        imgsz=640,
        verbose=False,
        retina_masks=True  # High-res masks for precise contours
    )[0]
    
    objects = []
    img_w, img_h = results.orig_shape  # Original image dimensions

    if results.masks is not None:
        for i in range(len(results)):
            # Get bounding box (still useful for UI)
            box = results.boxes[i]
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            conf = float(box.conf[0].cpu().numpy())
            cls = int(box.cls[0].cpu().numpy())
            label = _model.names[cls]
            
            # 🔥 GET CONTOUR from segmentation mask (the magic!)
            mask_xy = results.masks.xy[i].cpu().numpy()  # [[x1,y1], [x2,y2], ...]
            
            # Normalize contour points to 0-1 (for SVG viewBox)
            contour_normalized = [[float(pt[0]/img_w), float(pt[1]/img_h)] 
                                for pt in mask_xy]
            
            objects.append(DetectedObject(
                id=i,
                label=label,
                score=conf,
                bbox=BBox(x1=float(x1/img_w), y1=float(y1/img_h), 
                         x2=float(x2/img_w), y2=float(y2/img_h)),
                contour=contour_normalized  # 🔥 Exact object outline points!
            ))

    return DetectResponse(objects=objects)