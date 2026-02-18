"""
    Pydantic schema definitions used by the API layer.

    Re-exports request and response models for authentication, images,
    and hotspots so they can be imported from a single package namespace.
"""


from .images import ImageResponse, ImageCreate, ImageBase


__all__ = ["ImageResponse", "ImageCreate", "ImageBase"]