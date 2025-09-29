"""평가 서비스 테스트."""

from __future__ import annotations

from datetime import date, timedelta

from acen_api.models import ModelResult
from acen_api.repositories import CalendarRepository, DateRepository, FeedbackRepository, UserRepository
from acen_api.schemas import DateCreate, FeedbackCreate, UserCreate
from acen_api.services import EvaluatorService


def _create_user_and_calendar(db_session):
    user_repo = UserRepository(db_session)
    user = user_repo.create(UserCreate(username="eval"))
    db_session.flush()
    calendar_repo = CalendarRepository(db_session)
    calendar = calendar_repo.create(user_id=user.id, name="테스트")
    return user.id, calendar


def _add_date(db_session, calendar, user_id: int, day: date, done: int, total: int):
    repo = DateRepository(db_session)
    return repo.create(
        DateCreate(
            calendar_id=calendar.id,
            scheduled_date=day,
            schedule_done=done,
            schedule_total=total,
        ),
        user_id=user_id,
    )


def _add_feedback(db_session, date_entry, severity: float):
    repo = FeedbackRepository(db_session)
    return repo.create(
        FeedbackCreate(
            date_id=date_entry.id,
            title="평가",
            severity_score=severity,
        )
    )


def _add_model_result(db_session, date_entry: Date) -> ModelResult:
    model_result = ModelResult(date_id=date_entry.id, result_type="detect")
    db_session.add(model_result)
    db_session.flush()
    return model_result


def test_evaluator_metrics(db_session):
    user_id, calendar = _create_user_and_calendar(db_session)

    start = date(2024, 1, 1)
    for day_offset in range(3):
        entry = _add_date(db_session, calendar, user_id, start + timedelta(days=day_offset), done=1 + day_offset, total=3)
        _add_feedback(db_session, entry, severity=0.3 + 0.1 * day_offset)
        for _ in range(day_offset):
            _add_model_result(db_session, entry)

    service = EvaluatorService(db_session)
    metrics = service.evaluate_range(calendar.id, start, start + timedelta(days=2), user_id=user_id)

    assert metrics.adherence.current == metrics.adherence.current
    assert metrics.severity.current >= 0
    assert metrics.trend.current >= 0


def test_evaluator_empty(db_session):
    user_id, calendar = _create_user_and_calendar(db_session)
    service = EvaluatorService(db_session)

    metrics = service.evaluate_range(calendar.id, date(2024, 1, 1), date(2024, 1, 7), user_id=user_id)

    assert metrics.notes == "데이터가 없습니다."
    assert metrics.adherence.current == 0
