"""데이터베이스 세션 관리 유틸리티."""

from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session, sessionmaker

from ..config import AppSettings
from ..models import Base


settings = AppSettings()
engine = create_engine(settings.database_url, echo=False, future=True, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db() -> Generator[Session, None, None]:
    """요청 생명주기 동안 사용할 데이터베이스 세션을 제공."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """SQLite 경로를 준비하고 ORM 테이블을 생성."""
    _ensure_sqlite_path(settings.database_url)
    Base.metadata.create_all(bind=engine)


def _ensure_sqlite_path(database_url: str) -> None:
    """필요 시 SQLite 파일의 상위 디렉터리를 생성."""

    url = make_url(database_url)
    if url.get_backend_name() != "sqlite":
        return

    database = url.database
    if not database or database == ":memory:":
        return

    path = Path(database)
    if not path.is_absolute():
        path = Path.cwd() / path

    path.parent.mkdir(parents=True, exist_ok=True)
