"""FastAPI application entrypoint."""
from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import get_settings


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title=settings.APP_NAME,
        description="API for analyzing screenshots and generating bug reports",
        version="0.1.0",
    )

    # Include API router
    app.include_router(api_router, prefix=settings.API_PREFIX)

    return app


app = create_app()