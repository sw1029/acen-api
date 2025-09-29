"""피드백 및 추천 API."""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query

from ...repositories import DateRepository, FeedbackRepository, SuggestRepository
from ...schemas import ErrorResponse, FeedbackRead, SuggestRead
from ..deps import get_current_user, get_feedback_service, get_session, require_api_key


error_responses = {
    400: {"model": ErrorResponse, "description": "잘못된 요청"},
    404: {"model": ErrorResponse, "description": "데이터를 찾을 수 없습니다."},
}


router = APIRouter(prefix="/feedback", tags=["feedback"], responses=error_responses)


@router.get("/suggest", response_model=list[SuggestRead])
def list_suggestions(
    feedback_id: int = Query(...),
    top: int = Query(3, ge=1),
    session=Depends(get_session),
) -> list[SuggestRead]:
    repo = SuggestRepository(session)
    suggestions = repo.list_for_feedback(feedback_id)
    return suggestions[:top]


@router.post("/generate")
def generate_feedback(
    calendar_id: int = Query(...),
    start: date = Query(...),
    end: date = Query(...),
    service = Depends(get_feedback_service),
    user_id: int = Depends(get_current_user),
    _: None = Depends(require_api_key),
):
    result = service.generate_for_range(calendar_id, start, end, user_id=user_id)
    if not result:
        raise HTTPException(status_code=404, detail="No data available for feedback")
    return result


@router.get("/{date_id}", response_model=list[FeedbackRead])
def list_feedback(
    date_id: int,
    session=Depends(get_session),
    user_id: int = Depends(get_current_user),
) -> list[FeedbackRead]:
    date_repo = DateRepository(session)
    date = date_repo.get(date_id)
    if not date or date.user_id != user_id:
        raise HTTPException(status_code=404, detail="Date not found")
    repo = FeedbackRepository(session)
    return repo.list_for_date(date_id)
