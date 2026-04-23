from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["ping"])


class PingResponse(BaseModel):
    message: str


@router.get("/ping", response_model=PingResponse)
async def ping() -> PingResponse:
    return PingResponse(message="pong")
