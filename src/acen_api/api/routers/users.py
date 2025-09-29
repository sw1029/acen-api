"""사용자(User) API."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from ...repositories import UserRepository
from ...schemas import ErrorResponse, UserCreate, UserRead
from ..deps import get_session, require_api_key


error_responses = {
    400: {"model": ErrorResponse, "description": "잘못된 요청"},
    404: {"model": ErrorResponse, "description": "사용자를 찾을 수 없습니다."},
    401: {"model": ErrorResponse, "description": "인증 필요"},
}


router = APIRouter(prefix="/users", tags=["users"], responses=error_responses)


def _repo(session: Session) -> UserRepository:
    return UserRepository(session)


@router.get("", response_model=list[UserRead])
def list_users(session: Session = Depends(get_session), _: None = Depends(require_api_key)) -> list[UserRead]:
    return _repo(session).list()


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate,
    session: Session = Depends(get_session),
    _: None = Depends(require_api_key),
) -> UserRead:
    repo = _repo(session)
    user = repo.create(payload)
    session.commit()
    session.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    session: Session = Depends(get_session),
    _: None = Depends(require_api_key),
) -> Response:
    repo = _repo(session)
    user = repo.get(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    repo.delete(user)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
