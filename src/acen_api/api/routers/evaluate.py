"""평가지표 API."""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query

from ...schemas import ErrorResponse, EvaluatorMetrics
from ..deps import get_current_user, get_evaluator


error_responses = {
    400: {"model": ErrorResponse, "description": "잘못된 요청"},
    404: {"model": ErrorResponse, "description": "데이터를 찾을 수 없습니다."},
}


router = APIRouter(prefix="/evaluate", tags=["evaluate"], responses=error_responses)


@router.get("", response_model=EvaluatorMetrics)
def get_metrics(
    calendar_id: int = Query(...),
    start: date = Query(...),
    end: date = Query(...),
    evaluator = Depends(get_evaluator),
    user_id: int = Depends(get_current_user),
) -> EvaluatorMetrics:
    try:
        return evaluator.evaluate_range(calendar_id, start, end, user_id=user_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail="Calendar not found") from exc
