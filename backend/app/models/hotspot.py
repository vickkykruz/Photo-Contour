"""
    Hotspot model definition.

    Persists the association between a specific image region
    (bounding box or polygon coordinates) and the user-provided
    annotation text and link used in the interactive SVG output.
"""


from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.db.base import Base


class Hotspot(Base):
    __tablename__ = "hotspots"
    
    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(Integer, ForeignKey("images.id"), nullable=False)
    bbox_coords = Column(String)  # JSON string: [x1,y1,x2,y2]
    text_content = Column(String)
    link_url = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())