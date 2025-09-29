"""템플릿 및 스케줄 리소스 스키마."""

from __future__ import annotations

from typing import Annotated

from pydantic import Field

from .base import APIModel, TimestampModel


class ScheduleBase(APIModel):
    """공통 스케줄 속성."""

    title: Annotated[str, Field(max_length=120)]
    description: Annotated[str | None, Field(None)] = None
    order_index: Annotated[int, Field(ge=0)] = 0
    tags: Annotated[str | None, Field(None, max_length=120)] = None
    extra_info: Annotated[str | None, Field(None)] = None


class ScheduleCreate(ScheduleBase):
    """스케줄 생성 요청."""

    pass


class ScheduleUpdate(APIModel):
    """스케줄 수정 요청."""

    title: Annotated[str | None, Field(None, max_length=120)] = None
    description: Annotated[str | None, Field(None)] = None
    order_index: Annotated[int | None, Field(None, ge=0)] = None
    tags: Annotated[str | None, Field(None, max_length=120)] = None
    extra_info: Annotated[str | None, Field(None)] = None


class ScheduleRead(TimestampModel, ScheduleBase):
    """스케줄 응답 모델."""

    id: int
    template_id: int


class TemplateBase(APIModel):
    """공통 템플릿 속성."""

    name: Annotated[str, Field(max_length=100)]
    description: Annotated[str | None, Field(None)] = None
    theme: Annotated[str | None, Field(None, max_length=50)] = None


class TemplateCreate(TemplateBase):
    """템플릿 생성 요청."""

    schedules: list[ScheduleCreate] | None = None


class TemplateUpdate(APIModel):
    """템플릿 수정 요청."""

    name: Annotated[str | None, Field(None, max_length=100)] = None
    description: Annotated[str | None, Field(None)] = None
    theme: Annotated[str | None, Field(None, max_length=50)] = None
    schedules: list[ScheduleCreate] | None = None


class TemplateRead(TimestampModel, TemplateBase):
    """템플릿 응답 모델."""

    id: int
    schedules: list[ScheduleRead] | None = None
