"""FastAPI application entrypoint."""
from fastapi import FastAPI

from app.api.router import api_router


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Bug Report AI API",
        description="API for analyzing screenshots and generating bug reports",
        version="0.1.0",
    )

    # Include API router
    app.include_router(api_router, prefix="/api")

    return app


app = create_app()