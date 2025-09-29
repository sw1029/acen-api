"""모델 추론 API."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status

from ...schemas import (
    ClassificationRequest,
    ClassificationResponse,
    DetectionRequest,
    DetectionResponse,
    ErrorResponse,
    ImageReference,
)
from ..deps import get_classifier, get_detector


error_responses = {
    400: {"model": ErrorResponse, "description": "잘못된 입력"},
    404: {"model": ErrorResponse, "description": "이미지를 찾을 수 없습니다."},
}


router = APIRouter(prefix="/model", tags=["model"], responses=error_responses)


@router.post("/detect", response_model=DetectionResponse)
def detect(
    payload: DetectionRequest,
    detector = Depends(get_detector),
) -> DetectionResponse:
    detector.load()
    image_path = _resolve_image_path(payload)
    if not image_path.exists():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Image not found")

    boxes = detector.detect(image_path)
    return DetectionResponse(boxes=boxes)


@router.post("/classify", response_model=ClassificationResponse)
def classify(
    payload: ClassificationRequest,
    classifier = Depends(get_classifier),
) -> ClassificationResponse:
    classifier.load()
    image_path = _resolve_image_path(payload)
    if not image_path.exists():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Image not found")

    results = classifier.classify(image_path, top_k=payload.top_k)
    return ClassificationResponse(results=results)


def _resolve_image_path(payload: ImageReference) -> Path:
    if payload.image_path:
        return Path(payload.image_path)
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="image_path is required")
