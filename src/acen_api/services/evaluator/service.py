"""평가 도메인 서비스."""

from __future__ import annotations

from datetime import date

from sqlalchemy.orm import Session

from ...repositories import CalendarRepository, DateRepository
from ...schemas import EvaluatorMetrics
from .metrics import DailyRecord, compute_metrics


class EvaluatorService:
    """일자 로그와 모델 결과를 분석해 지표를 산출."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self.date_repo = DateRepository(session)
        self.calendar_repo = CalendarRepository(session)

    def evaluate_range(self, calendar_id: int, start: date, end: date, *, user_id: int) -> EvaluatorMetrics:
        calendar = self.calendar_repo.get(calendar_id)
        if not calendar or calendar.user_id != user_id:
            raise ValueError("calendar_not_accessible")

        records = []
        for date_obj in self.date_repo.list_by_range(calendar_id, start, end, user_id=user_id):
            severity_values = [feedback.severity_score for feedback in date_obj.feedback_entries if feedback.severity_score is not None]
            avg_severity = sum(severity_values) / len(severity_values) if severity_values else None
            record = DailyRecord(
                scheduled_date=date_obj.scheduled_date,
                completion_ratio=float(date_obj.completion_ratio),
                model_count=len(date_obj.model_results),
                severity_score=avg_severity,
            )
            records.append(record)

        return compute_metrics(records)
