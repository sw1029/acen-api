"""피드백 및 추천 스키마."""

from __future__ import annotations

from typing import Annotated

from pydantic import Field

from .base import APIModel, TimestampModel


class FeedbackBase(APIModel):
    """피드백 공통 속성."""

    title: Annotated[str, Field(max_length=120)]
    summary: str | None = None
    category: Annotated[str | None, Field(None, max_length=64)] = None
    severity_score: Annotated[float | None, Field(None, ge=0, le=1)] = None
    advice: str | None = None


class FeedbackCreate(FeedbackBase):
    """피드백 생성 요청."""

    date_id: int


class FeedbackRead(TimestampModel, FeedbackBase):
    """피드백 응답."""

    id: int
    date_id: int


class SuggestBase(APIModel):
    """추천 공통 속성."""

    product_id: int
    reason: str | None = None
    score: Annotated[float | None, Field(None, ge=0, le=1)] = None


class SuggestCreate(SuggestBase):
    """추천 생성 요청."""

    feedback_id: int


class SuggestRead(TimestampModel, SuggestBase):
    """추천 응답."""

    id: int
    feedback_id: int


class ProductBase(APIModel):
    """제품 공통 속성."""

    name: Annotated[str, Field(max_length=120)]
    brand: Annotated[str | None, Field(None, max_length=80)] = None
    tags: Annotated[str | None, Field(None, max_length=255)] = None
    description: str | None = None


class ProductCreate(ProductBase):
    """제품 생성 요청."""

    pass


class ProductUpdate(APIModel):
    """제품 수정 요청."""

    name: Annotated[str | None, Field(None, max_length=120)] = None
    brand: Annotated[str | None, Field(None, max_length=80)] = None
    tags: Annotated[str | None, Field(None, max_length=255)] = None
    description: str | None = None


class ProductRead(TimestampModel, ProductBase):
    """제품 응답."""

    id: int
