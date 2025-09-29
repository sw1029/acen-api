"""애플리케이션 전역 오류 처리."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from ..schemas import ErrorField, ErrorResponse


class ApplicationError(Exception):
    """도메인 계층에서 사용하는 기본 오류."""

    def __init__(
        self,
        message: str,
        *,
        code: str = "application_error",
        status_code: int = 400,
        detail: str | None = None,
        field_errors: list[ErrorField] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.status_code = status_code
        self.detail = detail
        self.field_errors = field_errors or []


def register_exception_handlers(app: FastAPI) -> None:
    """FastAPI 앱에 공통 예외 핸들러를 등록."""

    app.add_exception_handler(ApplicationError, _handle_application_error)  # type: ignore[arg-type]
    app.add_exception_handler(RequestValidationError, _handle_validation_error)
    app.add_exception_handler(StarletteHTTPException, _handle_http_exception)


def _handle_application_error(request: Request, exc: ApplicationError) -> JSONResponse:
    payload = ErrorResponse(
        code=exc.code,
        message=str(exc),
        detail=exc.detail,
        field_errors=exc.field_errors or None,
    )
    return JSONResponse(status_code=exc.status_code, content=payload.model_dump())


def _handle_validation_error(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    field_errors = [
        ErrorField(loc=list(error["loc"]), message=str(error["msg"]), type=error.get("type"))
        for error in exc.errors()
    ]
    payload = ErrorResponse(
        code="validation_error",
        message="요청 파라미터를 검증할 수 없습니다.",
        field_errors=field_errors,
    )
    return JSONResponse(status_code=422, content=payload.model_dump())


def _handle_http_exception(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    payload = ErrorResponse(
        code="http_error",
        message=exc.detail if isinstance(exc.detail, str) else str(exc.detail),
    )
    return JSONResponse(status_code=exc.status_code, content=payload.model_dump())
