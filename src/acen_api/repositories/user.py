"""사용자 리포지토리."""

from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import User
from ..schemas import UserCreate
from .base import BaseRepository


class UserRepository(BaseRepository):
    """사용자 CRUD."""

    def __init__(self, session: Session) -> None:
        super().__init__(session)

    def list(self) -> list[User]:
        stmt = select(User).order_by(User.id)
        return list(self.session.execute(stmt).scalars())

    def get(self, user_id: int) -> User | None:
        return self.session.get(User, user_id)

    def create(self, data: UserCreate | dict[str, Any]) -> User:
        payload = self._to_dict(data, exclude_none=True)
        user = User(**payload)
        self.session.add(user)
        self.session.flush()
        return user

    def delete(self, user: User) -> None:
        self.session.delete(user)

