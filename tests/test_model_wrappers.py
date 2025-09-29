"""모델 래퍼 스텁 동작 테스트."""

from __future__ import annotations

from PIL import Image

from acen_api.schemas import BoundingBox, ClassificationResult
from acen_api.services import (
    DummyDetector,
    ModelConfig,
    RuleBasedClassifier,
    UltralyticsDetector,
)
from acen_api.services.model import detector_ultralytics as yolo_module
from acen_api.services.model import device as device_module


def _prepare_image(tmp_path) -> Image.Image:
    path = tmp_path / "sample.png"
    Image.new("RGB", (100, 100), color="white").save(path)
    return path


def test_dummy_detector_detect(tmp_path):
    image_path = _prepare_image(tmp_path)

    model = DummyDetector(ModelConfig(name="dummy"))
    model.load(device="cpu")
    boxes = model.detect(image_path)

    assert boxes
    box = boxes[0]
    assert isinstance(box, BoundingBox)
    assert box.label == "acne"


def test_dummy_detector_classify(tmp_path):
    image_path = _prepare_image(tmp_path)
    model = DummyDetector(ModelConfig(name="dummy"))
    model.load()

    results = model.classify(image_path, top_k=1)

    assert len(results) == 1
    assert isinstance(results[0], ClassificationResult)


def test_choose_device_prefers_cuda(monkeypatch):
    class FakeCuda:
        @staticmethod
        def is_available() -> bool:
            return True

    class FakeTorch:
        cuda = FakeCuda()

    monkeypatch.setattr(device_module, "torch", FakeTorch())

    assert device_module.choose_device("cuda") == "cuda"


def test_ultralytics_detector_fallback(tmp_path, monkeypatch):
    monkeypatch.setattr(yolo_module, "YOLO", None)
    image_path = _prepare_image(tmp_path)
    model = UltralyticsDetector(ModelConfig(name="ultra", weights_path=tmp_path / "missing.pt"))
    model.load()

    boxes = model.detect(image_path)

    assert boxes
    assert isinstance(boxes[0], BoundingBox)


def test_rule_based_classifier(tmp_path):
    image_path = _prepare_image(tmp_path)
    classifier = RuleBasedClassifier()
    classifier.load()

    results = classifier.classify(image_path, top_k=2)

    assert len(results) == 2
    assert all(isinstance(item, ClassificationResult) for item in results)
