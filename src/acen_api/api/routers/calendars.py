"""캘린더(Calendar) 관련 API."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ...repositories import CalendarRepository
from ...schemas import CalendarCreate, CalendarRead, ErrorResponse
from ..deps import get_current_user, get_session, require_api_key


error_responses = {
    400: {"model": ErrorResponse, "description": "잘못된 요청"},
    404: {"model": ErrorResponse, "description": "리소스를 찾을 수 없습니다."},
}


router = APIRouter(prefix="/calendars", tags=["calendars"], responses=error_responses)


@router.get("", response_model=list[CalendarRead])
def list_calendars(
    session: Session = Depends(get_session),
    user_id: int = Depends(get_current_user),
) -> list[CalendarRead]:
    repo = CalendarRepository(session)
    return repo.list_by_user(user_id)


@router.post(
    "",
    response_model=CalendarRead,
    status_code=status.HTTP_201_CREATED,
)
def create_calendar(
    payload: CalendarCreate,
    session: Session = Depends(get_session),
    user_id: int = Depends(get_current_user),
    _: None = Depends(require_api_key),
) -> CalendarRead:
    repo = CalendarRepository(session)
    payload_user_id = payload.user_id or user_id
    if payload.user_id and payload.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user_id mismatch")
    cal = repo.create(user_id=payload_user_id, name=payload.name, description=payload.description)
    session.commit()
    session.refresh(cal)
    return cal
