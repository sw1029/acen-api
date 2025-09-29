"""모델 추론 요청과 응답 스키마."""

from __future__ import annotations

from typing import Annotated

from pydantic import Field

from .base import APIModel


class BoundingBox(APIModel):
    """탐지 결과 바운딩 박스."""

    x: float
    y: float
    width: float
    height: float
    score: Annotated[float, Field(ge=0, le=1)]
    label: str


class DetectionResponse(APIModel):
    """탐지 결과 응답."""

    boxes: list[BoundingBox]


class ClassificationResult(APIModel):
    """분류 결과 항목."""

    label: str
    score: Annotated[float, Field(ge=0, le=1)]


class ClassificationResponse(APIModel):
    """분류 결과 응답."""

    results: list[ClassificationResult]


class ImageReference(APIModel):
    """모델 입력으로 활용할 이미지 경로 또는 업로드 식별자."""

    image_path: str | None = None
    upload_id: str | None = None


class DetectionRequest(ImageReference):
    """탐지 요청."""

    confidence: Annotated[float, Field(ge=0, le=1)] = 0.25
    iou: Annotated[float, Field(ge=0, le=1)] = 0.45


class ClassificationRequest(ImageReference):
    """분류 요청."""

    top_k: Annotated[int, Field(ge=1, le=10)] = 3
