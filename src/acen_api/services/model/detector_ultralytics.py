"""Ultralytics YOLO 기반 탐지 래퍼."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

try:
    from ultralytics import YOLO
except ImportError:  # pragma: no cover - 옵셔널 의존성
    YOLO = None  # type: ignore[assignment]

from ...schemas import BoundingBox
from .base import ModelConfig, ModelWrapper
from .device import choose_device
from .dummy import DummyDetector

logger = logging.getLogger(__name__)


class UltralyticsDetector(ModelWrapper):
    """Ultralytics YOLO 모델을 감싼 래퍼.

    Ultralytics가 설치되어 있지 않거나 가중치가 없을 경우 내부적으로 DummyDetector로 폴백한다.
    """

    name = "ultralytics-detector"

    def __init__(self, config: ModelConfig | None = None) -> None:
        self.config = config or ModelConfig(name=self.name)
        self._model: Any | None = None
        self._labels: list[str] = []
        self._fallback = DummyDetector()
        self._loaded = False

    def load(self, *, device: str | None = None) -> None:
        target_device = choose_device(device or self.config.device)

        if YOLO is None:
            logger.warning("ultralytics 패키지를 찾을 수 없어 DummyDetector를 사용합니다.")
            self._fallback.load(device=target_device)
            self._model = None
            self._loaded = True
            return

        weights = self.config.weights_path
        if not weights or not Path(weights).exists():
            logger.warning("YOLO 가중치를 찾을 수 없어 DummyDetector로 대체합니다: %s", weights)
            self._fallback.load(device=target_device)
            self._model = None
            self._loaded = True
            return

        try:
            model = YOLO(str(weights))
            model.to(target_device)
            self._model = model
            self._labels = [str(v) for v in getattr(model, "names", {}).values()] if getattr(model, "names", None) else []
            self._loaded = True
        except Exception as exc:  # pragma: no cover - 외부 라이브러리 예외 처리
            logger.exception("YOLO 모델 로딩에 실패하여 DummyDetector로 전환합니다: %s", exc)
            self._fallback.load(device=target_device)
            self._model = None
            self._loaded = True

    def detect(self, image_path: Path) -> list[BoundingBox]:
        if not self._loaded:
            raise RuntimeError("모델이 로드되지 않았습니다. 먼저 load()를 호출하세요.")

        if self._model is None:
            return self._fallback.detect(image_path)

        try:
            results = self._model.predict(source=str(image_path), verbose=False)
        except Exception as exc:  # pragma: no cover - 예외 시 폴백
            logger.exception("YOLO 예측 실패, DummyDetector 결과 사용: %s", exc)
            return self._fallback.detect(image_path)

        boxes: list[BoundingBox] = []
        if not results:
            return boxes

        result = results[0]
        yolo_boxes = getattr(result, "boxes", None)
        if yolo_boxes is None:
            return boxes

        try:
            for box in yolo_boxes:
                xywh = box.xywh[0].tolist()
                cls_idx = int(box.cls[0].item()) if getattr(box, "cls", None) is not None else 0
                score = float(box.conf[0].item()) if getattr(box, "conf", None) is not None else 0.0
                label = self._labels[cls_idx] if self._labels and 0 <= cls_idx < len(self._labels) else str(cls_idx)
                boxes.append(
                    BoundingBox(
                        x=xywh[0],
                        y=xywh[1],
                        width=xywh[2],
                        height=xywh[3],
                        score=score,
                        label=label,
                    )
                )
        except Exception as exc:  # pragma: no cover - 변환 실패 시 폴백
            logger.exception("YOLO 결과 파싱 실패, DummyDetector 결과 사용: %s", exc)
            return self._fallback.detect(image_path)

        return boxes

    def classify(self, image_path: Path, top_k: int = 3):  # pragma: no cover - 탐지 전용
        return self._fallback.classify(image_path, top_k=top_k)
