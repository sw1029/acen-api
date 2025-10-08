"""FastAPI 의존성 공급자 정의."""

from __future__ import annotations

from collections.abc import Generator

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from ..core.db import get_db
from ..services import (
    EvaluatorService,
    FeedbackService,
    ImageStorageService,
    UltralyticsDetector,
    RuleBasedClassifier,
)
from ..config import AppSettings
from ..repositories import ApiKeyRepository, UserRepository


def get_session(db: Session = Depends(get_db)) -> Generator[Session, None, None]:
    yield db


def get_evaluator(session: Session = Depends(get_session)) -> EvaluatorService:
    return EvaluatorService(session)


def get_feedback_service(session: Session = Depends(get_session)) -> FeedbackService:
    return FeedbackService(session)


def get_storage() -> ImageStorageService:
    from pathlib import Path

    settings = AppSettings()
    storage_dir = Path("data/uploads")
    allowed = {ext.strip() for ext in settings.upload_allowed_ext.split(",") if ext.strip()}
    return ImageStorageService(
        storage_dir,
        allowed_extensions=allowed,
        max_file_size=settings.upload_max_bytes,
    )


def get_detector() -> UltralyticsDetector:
    return UltralyticsDetector()


def get_classifier() -> RuleBasedClassifier:
    return RuleBasedClassifier()


def get_api_key_repo(session: Session = Depends(get_session)) -> ApiKeyRepository:
    return ApiKeyRepository(session)


def require_api_key(
    x_api_key: str | None = Header(default=None),
    repo: ApiKeyRepository = Depends(get_api_key_repo),
) -> None:
    """DB에 저장된 API Key 유효성 검증."""

    active = repo.count_active()
    if active == 0:
        # 초기 상태에서는 키 없이 접근 허용
        return

    if not x_api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="API key required")

    api_key = repo.get_by_key(x_api_key)
    if not api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")


def get_user_repo(session: Session = Depends(get_session)) -> UserRepository:
    return UserRepository(session)


def get_current_user(
    user_repo: UserRepository = Depends(get_user_repo),
    x_user_id: str | None = Header(default=None),
) -> int:
    if x_user_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="X-User-Id header required")
    try:
        user_id = int(x_user_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="X-User-Id must be integer") from exc

    user = user_repo.get(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user_id
