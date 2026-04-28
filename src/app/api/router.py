from fastapi import APIRouter

from app.api.routes import echo, health, mentors, ping

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(ping.router)
api_router.include_router(echo.router)
api_router.include_router(mentors.router)
