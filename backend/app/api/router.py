"""Main API router that combines all route modules."""
from fastapi import APIRouter

from app.api.routes import health

api_router = APIRouter()

# Include route modules
api_router.include_router(health.router, tags=["health"])