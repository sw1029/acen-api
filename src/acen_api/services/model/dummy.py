"""더미 모델 구현."""

from __future__ import annotations

from pathlib import Path

from PIL import Image

from ...schemas import BoundingBox, ClassificationResult
from .base import ModelConfig, ModelWrapper


class DummyDetector(ModelWrapper):
    """테스트/초기 개발용 더미 탐지 모델."""

    name = "dummy-detector"

    def __init__(self, config: ModelConfig | None = None) -> None:
        self.config = config or ModelConfig(name=self.name)
        self.loaded = False

    def load(self, *, device: str | None = None) -> None:
        self.loaded = True

    def detect(self, image_path: Path) -> list[BoundingBox]:
        self._ensure_loaded()
        width, height = _read_image_size(image_path)
        return [
            BoundingBox(x=0.1 * width, y=0.1 * height, width=0.5 * width, height=0.5 * height, score=0.5, label="acne")
        ]

    def classify(self, image_path: Path, top_k: int = 3) -> list[ClassificationResult]:
        self._ensure_loaded()
        return [ClassificationResult(label="acne", score=0.6), ClassificationResult(label="clear", score=0.4)][:top_k]

    def _ensure_loaded(self) -> None:
        if not self.loaded:
            raise RuntimeError("모델이 로드되지 않았습니다. 먼저 load()를 호출하세요.")


class DummyClassifier(DummyDetector):
    """분류 전용 더미 모델."""

    name = "dummy-classifier"

    def detect(self, image_path: Path) -> list[BoundingBox]:  # pragma: no cover - 분류 전용에서 사용 안함
        return []


def _read_image_size(path: Path) -> tuple[int, int]:
    with Image.open(path) as img:
        return img.size
