from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(tags=["echo"])


class EchoRequest(BaseModel):
    text: str
    repeat: int = Field(ge=1, le=10)


class EchoResponse(BaseModel):
    result: str


@router.post("/echo", response_model=EchoResponse)
async def echo(payload: EchoRequest) -> EchoResponse:
    return EchoResponse(result=payload.text * payload.repeat)
