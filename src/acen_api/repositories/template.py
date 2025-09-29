"""템플릿/스케줄 관련 리포지토리."""

from __future__ import annotations

from typing import Any, Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..models import Schedule, Template
from ..schemas import ScheduleCreate, ScheduleUpdate, TemplateCreate, TemplateUpdate
from .base import BaseRepository


class TemplateRepository(BaseRepository):
    """템플릿 및 하위 스케줄을 관리."""

    def __init__(self, session: Session) -> None:
        super().__init__(session)

    def list(self) -> list[Template]:
        stmt = select(Template).options(selectinload(Template.schedules)).order_by(Template.id)
        return list(self.session.execute(stmt).unique().scalars())

    def get(self, template_id: int) -> Template | None:
        stmt = (
            select(Template)
            .options(selectinload(Template.schedules))
            .where(Template.id == template_id)
        )
        return self.session.execute(stmt).unique().scalar_one_or_none()

    def create(self, data: TemplateCreate | dict[str, Any]) -> Template:
        payload = self._to_dict(data, exclude_none=True)
        schedules_data = payload.pop("schedules", None) or []

        template = Template(**payload)
        self._apply_schedules(template, schedules_data)

        self.session.add(template)
        self.session.flush()
        return template

    def update(self, template: Template, data: TemplateUpdate | dict[str, Any]) -> Template:
        payload = self._to_dict(data, exclude_none=True)
        schedules_data = payload.pop("schedules", None)

        self._apply(template, payload)

        if schedules_data is not None:
            template.schedules[:] = []
            self._apply_schedules(template, schedules_data)

        self.session.flush()
        return template

    def delete(self, template: Template) -> None:
        self.session.delete(template)

    def _apply_schedules(
        self, template: Template, schedules_data: Iterable[ScheduleCreate | dict[str, Any]]
    ) -> None:
        for schedule_data in schedules_data:
            data_dict = self._to_dict(schedule_data, exclude_none=True)
            template.schedules.append(Schedule(**data_dict))


class ScheduleRepository(BaseRepository):
    """스케줄 단독 조작 리포지토리."""

    def __init__(self, session: Session) -> None:
        super().__init__(session)

    def get(self, schedule_id: int) -> Schedule | None:
        stmt = select(Schedule).where(Schedule.id == schedule_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def create(self, template_id: int, data: ScheduleCreate | dict[str, Any]) -> Schedule:
        payload = self._to_dict(data, exclude_none=True)
        schedule = Schedule(template_id=template_id, **payload)
        self.session.add(schedule)
        self.session.flush()
        return schedule

    def update(self, schedule: Schedule, data: ScheduleUpdate | dict[str, Any]) -> Schedule:
        payload = self._to_dict(data, exclude_none=True)
        self._apply(schedule, payload)
        self.session.flush()
        return schedule

    def delete(self, schedule: Schedule) -> None:
        self.session.delete(schedule)
