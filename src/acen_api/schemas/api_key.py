"""API Key 스키마."""

from __future__ import annotations

from typing import Annotated

from pydantic import Field

from .base import APIModel, TimestampModel


class ApiKeyBase(APIModel):
    """API Key 기본 필드."""

    description: Annotated[str | None, Field(None, max_length=255)] = None


class ApiKeyCreate(ApiKeyBase):
    """API Key 생성 요청."""

    pass


class ApiKeyRead(TimestampModel, ApiKeyBase):
    """API Key 응답."""

    id: int
    key: str | None = None
    revoked_at: str | None = None

