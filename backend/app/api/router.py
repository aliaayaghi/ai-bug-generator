"""Main API router that combines all route modules."""
from fastapi import APIRouter

from app.api.routes import health, reports

api_router = APIRouter()

# Include route modules
api_router.include_router(health.router, tags=["health"])
api_router.include_router(reports.router)