"""스토리지 서비스 테스트."""

from __future__ import annotations

from io import BytesIO

import pytest
from PIL import Image

from acen_api.services import ImageStorageService, StorageError


def _make_image_bytes(color: str = "red", fmt: str = "PNG") -> bytes:
    img = Image.new("RGB", (16, 16), color=color)
    buffer = BytesIO()
    img.save(buffer, format=fmt)
    return buffer.getvalue()


def test_save_bytes_creates_file(tmp_path):
    service = ImageStorageService(tmp_path)
    data = _make_image_bytes()

    result = service.save_bytes(data, filename="sample.png")

    assert result.path.exists()
    assert result.relative_path.suffix == ".png"
    assert result.content_type == "image/png"


def test_save_bytes_auto_extension(tmp_path):
    service = ImageStorageService(tmp_path)
    data = _make_image_bytes(fmt="JPEG")

    result = service.save_bytes(data)

    assert result.relative_path.suffix in {".jpg", ".jpeg"}


def test_rejects_invalid_extension(tmp_path):
    service = ImageStorageService(tmp_path)
    data = _make_image_bytes()

    with pytest.raises(StorageError):
        service.save_bytes(data, filename="evil.txt")


def test_rejects_large_file(tmp_path):
    service = ImageStorageService(tmp_path, max_file_size=10)
    data = b"1" * 11

    with pytest.raises(StorageError):
        service.save_bytes(data, filename="big.png")
