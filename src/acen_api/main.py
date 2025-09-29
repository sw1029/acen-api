"""acen API 서비스의 진입점."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from .api.routers import api_router
from .config import AppSettings
from .core.db import init_db
from .core.errors import register_exception_handlers


TAGS_METADATA = [
    {"name": "health", "description": "서비스 상태 확인"},
    {"name": "templates", "description": "스케줄 템플릿 및 항목 관리"},
    {"name": "dates", "description": "사용자 일정 수행 로그 관리"},
    {"name": "model", "description": "탐지/분류 모델 호출"},
    {"name": "evaluate", "description": "수행 지표 및 통계 조회"},
    {"name": "feedback", "description": "피드백 생성 및 추천 조회"},
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 시작/종료 처리를 위한 컨텍스트."""

    init_db()
    yield


def create_app() -> FastAPI:
    """FastAPI 애플리케이션을 생성하고 설정."""
    settings = AppSettings()
    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        lifespan=lifespan,
        openapi_tags=TAGS_METADATA,
    )

    app.include_router(api_router)

    # 정적 UI 서빙 (선택)
    if settings.ui_enabled:
        ui_dir = Path(__file__).resolve().parent / "ui"
        if ui_dir.exists():
            app.mount("/ui", StaticFiles(directory=str(ui_dir), html=True), name="ui")
    register_exception_handlers(app)

    return app


app = create_app()
