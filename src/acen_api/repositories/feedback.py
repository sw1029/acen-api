"""피드백/추천 리포지토리."""

from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..models import Feedback, Suggest
from ..schemas import FeedbackCreate, SuggestCreate
from .base import BaseRepository


class FeedbackRepository(BaseRepository):
    """피드백 생성 및 조회."""

    def __init__(self, session: Session) -> None:
        super().__init__(session)

    def create(self, data: FeedbackCreate | dict[str, Any]) -> Feedback:
        payload = self._to_dict(data, exclude_none=True)
        feedback = Feedback(**payload)
        self.session.add(feedback)
        self.session.flush()
        return feedback

    def list_for_date(self, date_id: int) -> list[Feedback]:
        stmt = (
            select(Feedback)
            .options(selectinload(Feedback.suggestions))
            .where(Feedback.date_id == date_id)
            .order_by(Feedback.id)
        )
        return list(self.session.execute(stmt).unique().scalars())

    def get(self, feedback_id: int) -> Feedback | None:
        stmt = (
            select(Feedback)
            .options(selectinload(Feedback.suggestions))
            .where(Feedback.id == feedback_id)
        )
        return self.session.execute(stmt).unique().scalar_one_or_none()

    def delete(self, feedback: Feedback) -> None:
        self.session.delete(feedback)


class SuggestRepository(BaseRepository):
    """추천 레코드 관리."""

    def __init__(self, session: Session) -> None:
        super().__init__(session)

    def create(self, data: SuggestCreate | dict[str, Any]) -> Suggest:
        payload = self._to_dict(data, exclude_none=True)
        suggestion = Suggest(**payload)
        self.session.add(suggestion)
        self.session.flush()
        return suggestion

    def list_for_feedback(self, feedback_id: int) -> list[Suggest]:
        stmt = select(Suggest).where(Suggest.feedback_id == feedback_id).order_by(Suggest.id)
        return list(self.session.execute(stmt).scalars())

    def delete(self, suggestion: Suggest) -> None:
        self.session.delete(suggestion)
