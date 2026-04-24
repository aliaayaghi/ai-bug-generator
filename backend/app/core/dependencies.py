"""FastAPI dependencies for dependency injection."""
from sqlalchemy.orm import Session

from app.db.session import get_db


# Re-export get_db for convenient imports in route files
# This allows routes to use: from app.core.dependencies import get_db
__all__ = ["get_db", "Session"]