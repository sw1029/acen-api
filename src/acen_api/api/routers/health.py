"""헬스 체크 라우터."""

from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["health"])


@router.get("", summary="API 상태 확인")
def health_check() -> dict[str, str]:
    """서비스 모니터링을 위한 간단한 OK 응답."""
    return {"status": "ok"}
