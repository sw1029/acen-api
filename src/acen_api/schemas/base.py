"""공용 Pydantic 기반 클래스와 유틸리티."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class APIModel(BaseModel):
    """공통 설정을 지닌 기본 모델."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class TimestampModel(APIModel):
    """조회 모델에서 공유하는 타임스탬프 필드."""

    created_at: datetime
    updated_at: datetime


class Pagination(APIModel):
    """간단한 페이징 메타데이터."""

    total: int
    page: int
    size: int
