"""공통 오류 응답 스키마."""

from __future__ import annotations

from typing import Annotated

from pydantic import Field

from .base import APIModel


class ErrorField(APIModel):
    """필드 단위 오류 정보를 표현."""

    loc: list[str | int]
    message: str
    type: Annotated[str | None, Field(None, max_length=100)] = None


class ErrorResponse(APIModel):
    """API 오류 응답 포맷."""

    code: Annotated[str, Field(max_length=64)]
    message: str
    detail: str | None = None
    field_errors: list[ErrorField] | None = None
