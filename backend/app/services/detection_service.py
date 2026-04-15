"""
    Object detection service.

    Wraps the computer vision model (e.g. Detectron2) used to
    automatically detect objects in an uploaded image and return
    their coordinates and labels for use in the studio UI.
"""


import os
import uuid
import tempfile
import requests
from pathlib import Path
from PIL import Image as PILImage

from app.schemas.hotspots import BBox, DetectedObject, DetectionResult


YOLO_SERVICE_URL = "http://localhost:8002/detect"


def run_yolo_detection(image_dict: dict) -> DetectionResult:
    """
    Run YOLOv8 detection on an image stored in Firebase Storage.

    Downloads the image to a temp file, sends it to the YOLO
    microservice, and returns the DetectionResult.
    """

    image_url = image_dict.get("url")
    image_id  = image_dict.get("id")

    if not image_url:
        raise ValueError("Image has no URL — cannot run detection.")

    # ── Download image from Firebase Storage to temp file ────────────────
    suffix   = os.path.splitext(image_dict.get("filename", "image.jpg"))[1] or ".jpg"
    tmp_path = os.path.join(tempfile.gettempdir(), f"yolo_{uuid.uuid4()}{suffix}")

    try:
        response = requests.get(image_url, timeout=30)
        response.raise_for_status()
        with open(tmp_path, "wb") as f:
            f.write(response.content)
    except requests.RequestException as e:
        raise RuntimeError(f"Failed to download image from Firebase Storage: {e}")

    try:
        # ── Get image dimensions ──────────────────────────────────────────
        pil_img = PILImage.open(tmp_path)
        img_width, img_height = pil_img.size

        # ── Call YOLO microservice ────────────────────────────────────────
        payload = {"image_path": tmp_path}
        try:
            resp = requests.post(YOLO_SERVICE_URL, json=payload, timeout=60)
        except requests.RequestException as e:
            raise RuntimeError(f"YOLO service unreachable: {e}")

        if resp.status_code != 200:
            raise RuntimeError(
                f"YOLO service error: {resp.status_code} {resp.text}"
            )

        data = resp.json()

        objects = [
            DetectedObject(
                id=o["id"],
                label=o["label"],
                score=o["score"],
                bbox=BBox(**o["bbox"]),
                contour=o.get("contour", [])
            )
            for o in data["objects"]
        ]

        return DetectionResult(
            image_id=image_id,
            objects=objects,
            width=img_width,
            height=img_height,
        )

    finally:
        # Always clean up temp file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)