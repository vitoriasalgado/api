from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError

from app.core.exceptions import DomainError


class ErrorBody(BaseModel):
    code: str
    message: str
    details: dict = {}


class ErrorResponse(BaseModel):
    error: ErrorBody


_STATUS_BY_CODE = {
    "NOT_FOUND": 404,
    "CONFLICT": 409,
    "BUSINESS_RULE_VIOLATION": 422,
    "DOMAIN_ERROR": 400,
}


def _payload(code: str, message: str, details: dict | None = None) -> dict:
    return ErrorResponse(
        error=ErrorBody(code=code, message=message, details=details or {})
    ).model_dump()


async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
    status = _STATUS_BY_CODE.get(exc.code, 400)
    return JSONResponse(status_code=status, content=_payload(exc.code, exc.message, exc.details))


async def integrity_error_handler(request: Request, exc: IntegrityError) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content=_payload("CONFLICT", "Database integrity constraint violated"),
    )


async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content=_payload("VALIDATION_ERROR", "Invalid request payload", {"errors": exc.errors()}),
    )


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(DomainError, domain_error_handler)
    app.add_exception_handler(IntegrityError, integrity_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
