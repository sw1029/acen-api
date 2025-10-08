"""API Key 발급 및 관리 API."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from ...repositories import ApiKeyRepository
from ...schemas import ApiKeyCreate, ApiKeyRead, ErrorResponse
from ..deps import get_api_key_repo, get_session


error_responses = {
    400: {"model": ErrorResponse, "description": "잘못된 요청"},
    401: {"model": ErrorResponse, "description": "API Key 필요"},
    404: {"model": ErrorResponse, "description": "API Key를 찾을 수 없습니다."},
}


router = APIRouter(prefix="/api-keys", tags=["api-keys"], responses=error_responses)


def _ensure_authorized(
    repo: ApiKeyRepository,
    x_api_key: str | None,
) -> None:
    if repo.count_active() == 0:
        return
    if not x_api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="API key required")
    if not repo.get_by_key(x_api_key):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")


@router.get("", response_model=list[ApiKeyRead])
def list_api_keys(
    repo: ApiKeyRepository = Depends(get_api_key_repo),
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
) -> list[ApiKeyRead]:
    _ensure_authorized(repo, x_api_key)
    keys = repo.list(include_revoked=True)
    return [
        ApiKeyRead(
            id=item.id,
            description=item.description,
            created_at=item.created_at,
            updated_at=item.updated_at,
            key=None,
            revoked_at=item.revoked_at.isoformat() if item.revoked_at else None,
        )
        for item in keys
    ]


@router.post("", response_model=ApiKeyRead, status_code=status.HTTP_201_CREATED)
def create_api_key(
    payload: ApiKeyCreate,
    repo: ApiKeyRepository = Depends(get_api_key_repo),
    session: Session = Depends(get_session),
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
) -> ApiKeyRead:
    _ensure_authorized(repo, x_api_key)
    api_key, raw = repo.create(description=payload.description)
    session.commit()
    session.refresh(api_key)
    return ApiKeyRead(
        id=api_key.id,
        description=api_key.description,
        created_at=api_key.created_at,
        updated_at=api_key.updated_at,
        key=raw,
        revoked_at=None,
    )


@router.delete("/{api_key_id}", status_code=status.HTTP_204_NO_CONTENT)
def revoke_api_key(
    api_key_id: int,
    repo: ApiKeyRepository = Depends(get_api_key_repo),
    session: Session = Depends(get_session),
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
):
    _ensure_authorized(repo, x_api_key)
    api_key = repo.get(api_key_id)
    if not api_key:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API key not found")
    repo.revoke(api_key)
    session.commit()
    return None
