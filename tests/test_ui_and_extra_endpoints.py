"""UI 및 추가 엔드포인트 스모크 테스트."""

from __future__ import annotations

from fastapi.testclient import TestClient
import os

from acen_api.api import deps
from acen_api.main import app
from acen_api.repositories import CalendarRepository, UserRepository
from acen_api.schemas import CalendarCreate, ProductCreate, UserCreate


def test_ui_served(db_session):
    def override_session():
        return db_session

    app.dependency_overrides[deps.get_session] = override_session
    with TestClient(app) as client:
        res = client.get("/ui")
        assert res.status_code == 200
        assert "acen Admin UI" in res.text
    app.dependency_overrides.clear()


def test_products_and_calendars_endpoints(db_session):
    def override_session():
        return db_session

    app.dependency_overrides[deps.get_session] = override_session
    with TestClient(app) as client:
        user = UserRepository(db_session).create(UserCreate(username="ui-user"))
        db_session.flush()
        headers = {"X-User-Id": str(user.id)}
        # products
        res = client.post(
            "/products", json={"name": "테스트 제품", "tags": "진정"}
        )
        assert res.status_code == 201
        res = client.get("/products")
        assert res.status_code == 200
        assert any(p["name"] == "테스트 제품" for p in res.json())

        # calendars
        res = client.post(
            "/calendars", json={"name": "캘린더A", "description": "테스트"}, headers=headers
        )
        assert res.status_code == 201
        res = client.get("/calendars", headers=headers)
        assert res.status_code == 200
    app.dependency_overrides.clear()


def test_api_key_protection(db_session, monkeypatch):
    # API_KEY 활성화 시 헤더 없으면 401
    monkeypatch.setenv("API_KEY", "secret")

    def override_session():
        return db_session

    app.dependency_overrides[deps.get_session] = override_session
    with TestClient(app) as client:
        r = client.post("/products", json={"name": "A"})
        assert r.status_code == 401
        r = client.post("/products", headers={"X-API-Key": "secret"}, json={"name": "A"})
        assert r.status_code in (201, 422)  # 최소 보호 확인 (필수 필드 부족 시 422 가능)
    app.dependency_overrides.clear()
