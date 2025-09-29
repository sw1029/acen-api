"""캘린더 및 일자 로그 스키마."""

from __future__ import annotations

from datetime import date

from typing import Annotated

from pydantic import Field

from .base import APIModel, TimestampModel
from .template import ScheduleRead


class CalendarBase(APIModel):
    """공통 캘린더 속성."""

    name: Annotated[str, Field(max_length=100)]
    description: Annotated[str | None, Field(None)] = None


class CalendarCreate(CalendarBase):
    """캘린더 생성 요청."""

    user_id: int | None = None


class CalendarUpdate(APIModel):
    """캘린더 수정 요청."""

    name: Annotated[str | None, Field(None, max_length=100)] = None
    description: Annotated[str | None, Field(None)] = None


class CalendarRead(TimestampModel, CalendarBase):
    """캘린더 응답 모델."""

    id: int
    user_id: int


class DateBase(APIModel):
    """공통 일자 로그 속성."""

    scheduled_date: date
    template_id: int | None = None
    completion_ratio: Annotated[float, Field(ge=0, le=1)] = 0.0
    schedule_done: Annotated[int, Field(ge=0)] = 0
    schedule_total: Annotated[int, Field(ge=0)] = 0
    notes: str | None = None
    image_path: str | None = None


class DateCreate(DateBase):
    """일자 로그 생성 요청."""

    calendar_id: int
    user_id: int | None = None


class DateRead(TimestampModel, DateBase):
    """일자 로그 응답."""

    id: int
    calendar_id: int
    user_id: int
    template: ScheduleRead | None = None
