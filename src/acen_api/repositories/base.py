"""공통 리포지토리 유틸."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel
from sqlalchemy.orm import Session


class BaseRepository:
    """세션을 보유하며 공통 도우미를 제공하는 리포지토리 기본 클래스."""

    def __init__(self, session: Session) -> None:
        self.session = session

    @staticmethod
    def _to_dict(data: Any, *, exclude_none: bool = False) -> dict[str, Any]:
        """Pydantic 모델 혹은 dict 유사체를 사전으로 변환."""

        if isinstance(data, BaseModel):
            return data.model_dump(exclude_unset=True, exclude_none=exclude_none)

        if isinstance(data, dict):
            raw = data
        else:
            raw = dict(data)
        if exclude_none:
            return {key: value for key, value in raw.items() if value is not None}
        return raw

    def _apply(self, instance: Any, data: dict[str, Any]) -> Any:
        """주어진 키/값을 인스턴스에 반영하고 반환."""

        for key, value in data.items():
            setattr(instance, key, value)
        return instance
