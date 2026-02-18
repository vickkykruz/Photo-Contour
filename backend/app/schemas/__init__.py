"""
    Pydantic schema definitions used by the API layer.

    Re-exports request and response models for authentication, images,
    and hotspots so they can be imported from a single package namespace.
"""


from .images import ImageResponse, ImageCreate, ImageBase
from .auth import UserCreate, UserLogin, Token, UserOut
from .hotspots import BBox, DetectedObject, DetectionResult, HotspotCreate, SvgResponse


__all__ = [
    "ImageResponse", "ImageCreate", "ImageBase",
    "UserCreate", "UserLogin", "Token", "UserOut",
    "BBox", "DetectedObject", "DetectionResult", "HotspotCreate", "SvgResponse",
]