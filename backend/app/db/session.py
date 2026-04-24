"""SQLAlchemy engine and session factory."""
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import get_settings

settings = get_settings()

# Create engine with SQLite-specific options
# check_same_thread=False allows the session to be used across different threads
# This is needed for FastAPI's async context
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=settings.APP_ENV == "development",
)

# Session factory - creates new Session instances
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db() -> Generator[Session, None, None]:
    """Get a database session.
    
    This is a generator function that FastAPI will use as a dependency.
    It yields a session and ensures it's closed after the request.
    
    Usage in routes:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()