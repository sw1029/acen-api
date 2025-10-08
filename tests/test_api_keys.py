"""API Key 발급/회수 테스트."""

from __future__ import annotations

from fastapi.testclient import TestClient

from acen_api.api import deps
from acen_api.main import app


def _override_session(db_session):
    def _inner():
        return db_session

    app.dependency_overrides[deps.get_session] = _inner


def test_api_key_lifecycle(db_session):
    _override_session(db_session)

    with TestClient(app) as client:
        # 최초 키 발급 (헤더 없이 허용)
        res = client.post("/api-keys", json={"description": "첫 키"})
        assert res.status_code == 201
        key = res.json()["key"]

        # 목록 조회 (발급된 키가 있어 헤더 필요)
        res = client.get("/api-keys")
        assert res.status_code == 401

        res = client.get("/api-keys", headers={"X-API-Key": key})
        assert res.status_code == 200
        data = res.json()
        assert len(data) == 1

        key_id = data[0]["id"]

        # 키 회수
        res = client.delete(f"/api-keys/{key_id}", headers={"X-API-Key": key})
        assert res.status_code == 204

        # 회수 후 활성 키가 없으므로 누구나 접근 가능(빈 목록)
        res = client.get("/api-keys")
        assert res.status_code == 200
        assert res.json()[0]["revoked_at"] is not None

    app.dependency_overrides.clear()
