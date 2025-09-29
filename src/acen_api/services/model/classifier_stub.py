"""간단 규칙 기반 분류 스텁."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageStat

from ...schemas import BoundingBox, ClassificationResult
from .base import ModelConfig, ModelWrapper


class RuleBasedClassifier(ModelWrapper):
    """간단한 통계 기반 더미 분류기.

    평균 밝기 등을 기반으로 가중치를 생성하여 초기 API 연동을 돕는다.
    """

    name = "rule-based-classifier"

    def __init__(self, config: ModelConfig | None = None) -> None:
        self.config = config or ModelConfig(name=self.name)
        self._loaded = False

    def load(self, *, device: str | None = None) -> None:
        self._loaded = True

    def detect(self, image_path: Path) -> list[BoundingBox]:  # pragma: no cover - 분류 전용
        return []

    def classify(self, image_path: Path, top_k: int = 3) -> list[ClassificationResult]:
        if not self._loaded:
            raise RuntimeError("모델이 로드되지 않았습니다. 먼저 load()를 호출하세요.")

        with Image.open(image_path) as img:
            stat = ImageStat.Stat(img.convert("L"))
            mean_brightness = stat.mean[0] / 255.0

        # 밝을수록 "clear" 점수 상승, 어두울수록 "acne" 점수 상승
        acne_score = max(0.0, min(1.0, 1.0 - mean_brightness))
        clear_score = max(0.0, min(1.0, mean_brightness))
        neutral_score = 1.0 - abs(clear_score - acne_score)

        results = [
            ClassificationResult(label="acne", score=float(acne_score)),
            ClassificationResult(label="clear", score=float(clear_score)),
            ClassificationResult(label="neutral", score=float(neutral_score)),
        ]

        results.sort(key=lambda item: item.score, reverse=True)
        return results[:top_k]
