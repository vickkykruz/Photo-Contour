"""
    Pydantic models for image upload and retrieval.

    Defines schemas for image metadata, upload responses, and
    list/detail views returned by the image-related API endpoints.
"""


from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ImageBase(BaseModel):
    filename: str
    filepath: str
    
    
class ImageCreate(BaseModel):
    filename: str
    
    
class ImageResponse(ImageBase):
    id: int
    width: Optional[int] = None
    height: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True