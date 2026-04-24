"""SQLAlchemy declarative base for database models."""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all database models.
    
    All models should inherit from this class to ensure proper
    table creation and relationship handling.
    """
    pass