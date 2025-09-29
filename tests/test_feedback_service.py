"""피드백 서비스 통합 테스트."""

from __future__ import annotations

from datetime import date

import pytest

from acen_api.repositories import CalendarRepository, ProductRepository, UserRepository
from acen_api.schemas import DateCreate, FeedbackCreate, ProductCreate, UserCreate
from acen_api.services import FeedbackService


@pytest.fixture()
def setup_user(db_session):
    repo = UserRepository(db_session)
    user = repo.create(UserCreate(username="feedback-user"))
    db_session.flush()
    return user.id


@pytest.fixture()
def setup_calendar(db_session, setup_user):
    calendar = CalendarRepository(db_session).create(
        user_id=setup_user, name="사용자"
    )
    return calendar


@pytest.fixture()
def seed_products(db_session):
    repo = ProductRepository(db_session)
    repo.create(ProductCreate(name="진정 앰플", tags="진정"))
    repo.create(ProductCreate(name="보습 크림", tags="보습"))
    repo.create(ProductCreate(name="유지 토너", tags="유지"))


def _add_date_with_feedback(db_session, calendar, scheduled_date: date, done: int, total: int, severity: float, user_id: int):
    from acen_api.repositories import DateRepository, FeedbackRepository

    date_repo = DateRepository(db_session)
    entry = date_repo.create(
        DateCreate(
            calendar_id=calendar.id,
            scheduled_date=scheduled_date,
            schedule_done=done,
            schedule_total=total,
        ),
        user_id=user_id,
    )

    FeedbackRepository(db_session).create(
        FeedbackCreate(
            date_id=entry.id,
            title="기존",
            severity_score=severity,
        )
    )
    return entry


def test_feedback_service_generates_plan(db_session, setup_calendar, seed_products, setup_user):
    calendar = setup_calendar

    _add_date_with_feedback(
        db_session, calendar, date(2024, 1, 1), done=1, total=4, severity=0.2, user_id=setup_user
    )
    _add_date_with_feedback(
        db_session, calendar, date(2024, 1, 2), done=1, total=4, severity=0.4, user_id=setup_user
    )

    service = FeedbackService(db_session)
    result = service.generate_for_range(calendar.id, date(2024, 1, 1), date(2024, 1, 2), user_id=setup_user)

    assert result is not None
    assert result.feedback_id > 0
    assert result.suggestion_ids


def test_feedback_service_returns_none_when_no_data(db_session, setup_calendar, setup_user):
    calendar = setup_calendar
    service = FeedbackService(db_session)

    result = service.generate_for_range(calendar.id, date(2024, 1, 1), date(2024, 1, 7), user_id=setup_user)

    assert result is None
