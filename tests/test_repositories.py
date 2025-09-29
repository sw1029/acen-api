"""리포지토리 계층 동작 테스트."""

from __future__ import annotations

from datetime import date

import pytest

from acen_api.models import Calendar, Schedule
from acen_api.repositories import (
    CalendarRepository,
    DateRepository,
    FeedbackRepository,
    ProductRepository,
    ScheduleRepository,
    SuggestRepository,
    TemplateRepository,
    UserRepository,
)
from acen_api.schemas import (
    DateCreate,
    FeedbackCreate,
    ProductCreate,
    ProductUpdate,
    ScheduleCreate,
    ScheduleUpdate,
    SuggestCreate,
    TemplateCreate,
    TemplateUpdate,
    UserCreate,
)


def _create_user(db_session) -> int:
    repo = UserRepository(db_session)
    user = repo.create(UserCreate(username="tester"))
    db_session.flush()
    return user.id


def test_template_create_and_update(db_session):
    repo = TemplateRepository(db_session)

    template = repo.create(
        TemplateCreate(
            name="아침 루틴",
            description="피부 컨디션 준비",
            schedules=[
                ScheduleCreate(title="세안", order_index=0),
                ScheduleCreate(title="토너", order_index=1),
            ],
        )
    )

    assert template.id is not None
    assert len(template.schedules) == 2
    assert {s.title for s in template.schedules} == {"세안", "토너"}

    repo.update(
        template,
        TemplateUpdate(
            name="저녁 루틴",
            schedules=[ScheduleCreate(title="클렌징", order_index=0)],
        ),
    )

    assert template.name == "저녁 루틴"
    assert len(template.schedules) == 1
    assert template.schedules[0].title == "클렌징"


def test_schedule_crud(db_session):
    template = TemplateRepository(db_session).create(
        TemplateCreate(name="베이스", schedules=[])
    )

    schedule_repo = ScheduleRepository(db_session)
    schedule = schedule_repo.create(template.id, ScheduleCreate(title="테스트", order_index=0))

    schedule_repo.update(schedule, ScheduleUpdate(order_index=2, tags="테스트"))

    assert schedule.order_index == 2
    assert schedule.tags == "테스트"

    schedule_repo.delete(schedule)
    db_session.flush()
    assert db_session.get(Schedule, schedule.id) is None


def test_date_repository_create_and_list(db_session):
    user_id = _create_user(db_session)
    calendar_repo = CalendarRepository(db_session)
    calendar = calendar_repo.create(user_id=user_id, name="사용자1")

    date_repo = DateRepository(db_session)
    first = date_repo.create(
        DateCreate(
            calendar_id=calendar.id,
            scheduled_date=date(2024, 1, 1),
            schedule_done=1,
            schedule_total=2,
        ),
        user_id=user_id,
    )
    second = date_repo.create(
        DateCreate(
            calendar_id=calendar.id,
            scheduled_date=date(2024, 1, 2),
            schedule_done=2,
            schedule_total=2,
        ),
        user_id=user_id,
    )

    assert pytest.approx(first.completion_ratio) == 0.5
    assert second.completion_ratio == 1.0

    results = date_repo.list_by_range(
        calendar_id=calendar.id,
        start_date=date(2023, 12, 31),
        end_date=date(2024, 1, 3),
        user_id=user_id,
    )

    assert [item.id for item in results] == [first.id, second.id]


def test_product_repository_search_and_update(db_session):
    repo = ProductRepository(db_session)

    calming = repo.create(
        ProductCreate(name="카밍 토너", tags="진정,토너", description="민감 피부")
    )
    repo.create(ProductCreate(name="클렌저", tags="세안"))

    results = repo.search_by_tag("진정")
    assert len(results) == 1
    assert results[0].id == calming.id

    repo.update(calming, ProductUpdate(description="피부 진정용"))
    assert calming.description == "피부 진정용"


def test_feedback_and_suggest_repositories(db_session):
    user_id = _create_user(db_session)
    calendar_repo = CalendarRepository(db_session)
    calendar = calendar_repo.create(user_id=user_id, name="캘린더")

    date_repo = DateRepository(db_session)
    date_entry = date_repo.create(
        DateCreate(calendar_id=calendar.id, scheduled_date=date.today()),
        user_id=user_id,
    )

    product = ProductRepository(db_session).create(ProductCreate(name="보습제"))

    feedback_repo = FeedbackRepository(db_session)
    feedback = feedback_repo.create(
        FeedbackCreate(
            date_id=date_entry.id,
            title="보습 강화",
            summary="건조함 개선 필요",
            severity_score=0.4,
        )
    )

    suggest_repo = SuggestRepository(db_session)
    suggest_repo.create(
        SuggestCreate(feedback_id=feedback.id, product_id=product.id, reason="보습 강조")
    )

    feedbacks = feedback_repo.list_for_date(date_entry.id)
    assert len(feedbacks) == 1
    assert feedbacks[0].suggestions[0].reason == "보습 강조"

    suggestions = suggest_repo.list_for_feedback(feedback.id)
    assert len(suggestions) == 1
    assert suggestions[0].product_id == product.id
