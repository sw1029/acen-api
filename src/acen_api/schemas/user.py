"""사용자 스키마."""

from __future__ import annotations

from typing import Annotated

from pydantic import Field

from .base import APIModel, TimestampModel


class UserBase(APIModel):
    """사용자 공통 필드."""

    external_id: Annotated[str | None, Field(None, max_length=64)] = None
    username: Annotated[str | None, Field(None, max_length=64)] = None
    display_name: Annotated[str | None, Field(None, max_length=120)] = None
    email: Annotated[str | None, Field(None, max_length=255)] = None


class UserCreate(UserBase):
    """사용자 생성 요청."""

    pass


class UserRead(TimestampModel, UserBase):
    """사용자 응답."""

    id: int

