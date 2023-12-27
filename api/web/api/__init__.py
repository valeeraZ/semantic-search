"""API for the application."""
from fastapi.routing import APIRouter

from api.web.api import file, monitoring

api_router = APIRouter()
api_router.include_router(monitoring.router)
api_router.include_router(file.router)
