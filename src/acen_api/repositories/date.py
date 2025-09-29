"""캘린더/일자 관련 리포지토리."""

from __future__ import annotations

from datetime import date
from typing import Any

from sqlalchemy import and_, select
from sqlalchemy.orm import Session, selectinload

from ..models import Calendar, Date
from ..schemas import DateCreate
from .base import BaseRepository


class CalendarRepository(BaseRepository):
    """캘린더 생성 및 조회 리포지토리."""

    def __init__(self, session: Session) -> None:
        super().__init__(session)

    def create(self, *, user_id: int, name: str, description: str | None = None) -> Calendar:
        calendar = Calendar(name=name, description=description, user_id=user_id)
        self.session.add(calendar)
        self.session.flush()
        return calendar

    def get(self, calendar_id: int) -> Calendar | None:
        stmt = select(Calendar).where(Calendar.id == calendar_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def list(self) -> list[Calendar]:
        stmt = select(Calendar).order_by(Calendar.id)
        return list(self.session.execute(stmt).scalars())

    def list_by_user(self, user_id: int) -> list[Calendar]:
        stmt = select(Calendar).where(Calendar.user_id == user_id).order_by(Calendar.id)
        return list(self.session.execute(stmt).scalars())


class DateRepository(BaseRepository):
    """일자 로그 CRUD 및 조회."""

    def __init__(self, session: Session) -> None:
        super().__init__(session)

    def create(self, data: DateCreate | dict[str, Any], *, user_id: int) -> Date:
        payload = self._to_dict(data)
        payload["user_id"] = user_id
        completion_ratio = self._calc_ratio(
            payload.get("schedule_done", 0), payload.get("schedule_total", 0)
        )
        payload.setdefault("completion_ratio", completion_ratio)

        date_obj = Date(**payload)
        self.session.add(date_obj)
        self.session.flush()
        return date_obj

    def get(self, date_id: int) -> Date | None:
        stmt = (
            select(Date)
            .options(
                selectinload(Date.model_results),
                selectinload(Date.feedback_entries),
                selectinload(Date.template),
            )
            .where(Date.id == date_id)
        )
        return self.session.execute(stmt).unique().scalar_one_or_none()

    def list_by_range(
        self, calendar_id: int, start_date: date, end_date: date, *, user_id: int | None = None
    ) -> list[Date]:
        stmt = (
            select(Date)
            .options(selectinload(Date.model_results), selectinload(Date.feedback_entries))
            .where(
                and_(
                    Date.calendar_id == calendar_id,
                    Date.scheduled_date >= start_date,
                    Date.scheduled_date <= end_date,
                )
            )
            .order_by(Date.scheduled_date)
        )
        if user_id is not None:
            stmt = stmt.where(Date.user_id == user_id)
        return list(self.session.execute(stmt).unique().scalars())

    def update(self, date_obj: Date, data: dict[str, Any]) -> Date:
        payload = self._to_dict(data)
        if "schedule_done" in payload or "schedule_total" in payload:
            done = payload.get("schedule_done", date_obj.schedule_done)
            total = payload.get("schedule_total", date_obj.schedule_total)
            payload["completion_ratio"] = self._calc_ratio(done, total)
        self._apply(date_obj, payload)
        self.session.flush()
        return date_obj

    @staticmethod
    def _calc_ratio(done: int, total: int) -> float:
        if total <= 0:
            return 0.0
        ratio = done / total
        return max(0.0, min(1.0, ratio))
