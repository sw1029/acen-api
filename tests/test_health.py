"""헬스 체크 엔드포인트 스모크 테스트."""

from fastapi.testclient import TestClient

from acen_api.main import app


client = TestClient(app)


def test_health_ok() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
