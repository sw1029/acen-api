"""업로드 엔드포인트 테스트."""

from __future__ import annotations

import io
import os

from PIL import Image
from fastapi.testclient import TestClient

from acen_api.api import deps
from acen_api.main import app


def _image_bytes(fmt: str = "PNG") -> bytes:
    bio = io.BytesIO()
    Image.new("RGB", (8, 8), color="red").save(bio, format=fmt)
    return bio.getvalue()


def test_upload_image_requires_key(db_session):
    def override_session():
        return db_session

    app.dependency_overrides[deps.get_session] = override_session
    with TestClient(app) as client:
        key = client.post("/api-keys", json={"description": "upload"}).json()["key"]
        files = {"file": ("a.png", _image_bytes(), "image/png")}
        r = client.post("/uploads", files=files)
        assert r.status_code == 401
        r = client.post("/uploads", files=files, headers={"X-API-Key": key})
        assert r.status_code == 200
        assert r.json()["relative_path"].endswith(".png")
    app.dependency_overrides.clear()


def test_upload_image_size_limit(db_session, monkeypatch):
    monkeypatch.setenv("UPLOAD_MAX_BYTES", "10")

    def override_session():
        return db_session

    app.dependency_overrides[deps.get_session] = override_session
    with TestClient(app) as client:
        key = client.post("/api-keys", json={"description": "upload"}).json()["key"]
        files = {"file": ("a.png", b"1" * 20, "image/png")}
        r = client.post("/uploads", files=files, headers={"X-API-Key": key})
        assert r.status_code == 400
    app.dependency_overrides.clear()
