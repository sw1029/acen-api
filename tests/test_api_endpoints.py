"""FastAPI 엔드포인트 스모크 테스트."""

from __future__ import annotations

from datetime import date

import pytest
from fastapi.testclient import TestClient

from acen_api.api import deps
from acen_api.main import app
from acen_api.repositories import CalendarRepository, ProductRepository, UserRepository
from acen_api.schemas import ProductCreate, UserCreate


@pytest.fixture()
def client(db_session):
    def override_session():
        return db_session

    app.dependency_overrides[deps.get_session] = override_session

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_template_crud(client, db_session):
    payload = {
        "name": "테스트 템플릿",
        "description": "루틴",
        "schedules": [
            {"title": "세안", "order_index": 0},
            {"title": "토너", "order_index": 1},
        ],
    }

    response = client.post("/templates", json=payload)
    assert response.status_code == 201
    template_id = response.json()["id"]

    response = client.get("/templates")
    assert response.status_code == 200
    templates = response.json()
    assert len(templates) == 1
    assert templates[0]["id"] == template_id


def test_dates_and_feedback_flow(client, db_session):
    user_repo = UserRepository(db_session)
    user = user_repo.create(UserCreate(username="api-user"))
    db_session.flush()
    headers = {"X-User-Id": str(user.id)}

    calendar = CalendarRepository(db_session).create(user_id=user.id, name="사용자")
    ProductRepository(db_session).create(ProductCreate(name="진정 토너", tags="진정"))
    db_session.commit()

    # 일자 로그를 생성
    for idx in range(2):
        payload = {
            "calendar_id": calendar.id,
            "scheduled_date": date(2024, 1, idx + 1).isoformat(),
            "schedule_done": idx,
            "schedule_total": 2,
        }
        response = client.post("/dates", json=payload, headers=headers)
        assert response.status_code == 201

    params = {
        "calendar_id": calendar.id,
        "start": date(2024, 1, 1).isoformat(),
        "end": date(2024, 1, 2).isoformat(),
    }
    response = client.get("/dates", params=params, headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 2

    response = client.get("/evaluate", params=params, headers=headers)
    assert response.status_code == 200
    metrics = response.json()
    assert "adherence" in metrics

    response = client.post("/feedback/generate", params=params, headers=headers)
    assert response.status_code in (200, 404)
    if response.status_code == 200:
        body = response.json()
        assert body["feedback_id"] > 0
        response = client.get("/feedback/suggest", params={"feedback_id": body["feedback_id"]})
        assert response.status_code == 200, response.json()
