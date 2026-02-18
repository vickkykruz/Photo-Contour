"""
    SQLAlchemy ORM model package.

    Exposes the declarative Base and collects all table models
    (user, image, hotspot) so Alembic can discover them for migrations.
"""


from .user import User
from .image import Image
from .hotspot import Hotspot


__all__ = ["User", "Image", "Hotspot"]