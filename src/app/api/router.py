from fastapi import APIRouter

from app.api.routes import aluno, echo, health, materia, mentors, nota, ping

api_router = APIRouter()
api_router.include_router(aluno.router)
api_router.include_router(health.router)
api_router.include_router(ping.router)
api_router.include_router(echo.router)
api_router.include_router(mentors.router)
api_router.include_router(materia.router)
api_router.include_router(nota.router)
