"""모델 래퍼 인터페이스 정의."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Protocol

from ...schemas import BoundingBox, ClassificationResult


class ModelWrapper(Protocol):
    """탐지/분류 모델 공통 인터페이스."""

    name: str

    def load(self, *, device: str | None = None) -> None:  # pragma: no cover - 인터페이스 선언
        """모델 리소스를 메모리에 로드."""

    def detect(self, image_path: Path) -> list[BoundingBox]:  # pragma: no cover
        """탐지 결과 반환."""

    def classify(self, image_path: Path, top_k: int = 3) -> list[ClassificationResult]:  # pragma: no cover
        """분류 결과 반환."""


@dataclass(slots=True)
class ModelConfig:
    """모델 초기화에 필요한 설정."""

    name: str
    weights_path: Path | None = None
    labels: Iterable[str] | None = None
    device: str | None = None
