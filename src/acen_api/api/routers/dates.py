"""일자 로그 관련 API."""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ...repositories import CalendarRepository, DateRepository
from ...schemas import DateCreate, DateRead, ErrorResponse
from ..deps import get_current_user, get_session, require_api_key


error_responses = {
    400: {"model": ErrorResponse, "description": "잘못된 요청"},
    404: {"model": ErrorResponse, "description": "리소스를 찾을 수 없습니다."},
}


router = APIRouter(prefix="/dates", tags=["dates"], responses=error_responses)


@router.post(
    "",
    response_model=DateRead,
    status_code=status.HTTP_201_CREATED,
)
def create_date(
    payload: DateCreate,
    session: Session = Depends(get_session),
    user_id: int = Depends(get_current_user),
    _: None = Depends(require_api_key),
) -> DateRead:
    cal_repo = CalendarRepository(session)
    calendar = cal_repo.get(payload.calendar_id)
    if not calendar or calendar.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Calendar not found")

    if payload.user_id and payload.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user_id mismatch")

    repo = DateRepository(session)
    date_entry = repo.create(payload, user_id=user_id)
    session.commit()
    session.refresh(date_entry)
    return date_entry


@router.get("", response_model=list[DateRead])
def list_dates(
    calendar_id: int = Query(...),
    start: date = Query(...),
    end: date = Query(...),
    session: Session = Depends(get_session),
    user_id: int = Depends(get_current_user),
) -> list[DateRead]:
    if start > end:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="start must be before end")

    repo = DateRepository(session)
    entries = repo.list_by_range(calendar_id, start, end, user_id=user_id)
    return entries
