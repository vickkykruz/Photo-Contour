"""
    Image model definition.

    Stores metadata for uploaded images, such as owner, file path,
    dimensions, and related hotspots created in the studio.
"""


from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class Image(Base):
    __tablename__ = "images"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    filepath = Column(String, nullable=False)  # path to static/uploads/
    user_id = Column(Integer, ForeignKey("users.id"))
    width = Column(Integer)
    height = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships (added later)