"""
    Database initialization helpers.

    Provides functions to create database tables, seed initial data,
    and run any one-time setup required when the application starts.
"""


from app.db.base import Base, engine
from app.models import User, Image, Hotspot


def init_db():
    """Create all tables in the database."""
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")

if __name__ == "__main__":
    init_db()