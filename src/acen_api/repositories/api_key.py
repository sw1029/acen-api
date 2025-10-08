"""API Key 리포지토리."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import ApiKey
from .base import BaseRepository


class ApiKeyRepository(BaseRepository):
    """API Key CRUD 및 검증."""

    def __init__(self, session: Session) -> None:
        super().__init__(session)

    def list(self, include_revoked: bool = False) -> list[ApiKey]:
        stmt = select(ApiKey).order_by(ApiKey.id)
        if not include_revoked:
            stmt = stmt.where(ApiKey.revoked_at.is_(None))
        return list(self.session.execute(stmt).scalars())

    def count_active(self) -> int:
        stmt = select(ApiKey).where(ApiKey.revoked_at.is_(None))
        return len(self.session.execute(stmt).scalars().all())

    def get(self, api_key_id: int) -> ApiKey | None:
        return self.session.get(ApiKey, api_key_id)

    def create(self, *, description: str | None = None, key: str | None = None) -> tuple[ApiKey, str]:
        raw_key = key or self._generate_key()
        api_key = ApiKey(key=raw_key, description=description)
        self.session.add(api_key)
        self.session.flush()
        return api_key, raw_key

    def get_by_key(self, key: str) -> ApiKey | None:
        stmt = select(ApiKey).where(ApiKey.key == key, ApiKey.revoked_at.is_(None))
        return self.session.execute(stmt).scalar_one_or_none()

    def revoke(self, api_key: ApiKey) -> None:
        api_key.revoked_at = datetime.now(timezone.utc)
        self.session.flush()

    @staticmethod
    def _generate_key(length: int = 48) -> str:
        import secrets
        import string

        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))
