"""이미지 스토리지 서비스."""

from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Iterable
from uuid import uuid4

from PIL import Image, ImageOps


class StorageError(Exception):
    """스토리지 조작 실패 시 발생하는 예외."""


@dataclass(slots=True)
class StorageResult:
    """저장된 파일에 대한 메타데이터."""

    path: Path
    relative_path: Path
    content_type: str


class ImageStorageService:
    """이미지 저장/검증을 담당하는 서비스."""

    def __init__(
        self,
        base_dir: Path,
        *,
        allowed_extensions: Iterable[str] | None = None,
        max_file_size: int = 5 * 1024 * 1024,
        normalize_orientation: bool = True,
    ) -> None:
        self.base_dir = Path(base_dir)
        self.allowed_extensions = {
            ext.lower().lstrip(".") for ext in (allowed_extensions or {"jpg", "jpeg", "png", "webp"})
        }
        self.max_file_size = max_file_size
        self.normalize_orientation = normalize_orientation

        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save_bytes(self, data: bytes, *, filename: str | None = None) -> StorageResult:
        """바이트 데이터를 검증 후 저장."""

        self._validate_size(len(data))

        image = self._load_image(data)
        extension = self._resolve_extension(filename, image)
        self._validate_extension(extension)

        content_type = self._guess_content_type(extension)
        file_name = f"{uuid4().hex}.{extension}"
        full_path = self.base_dir / file_name

        image_to_save = image
        if self.normalize_orientation:
            image_to_save = ImageOps.exif_transpose(image)

        buffer = BytesIO()
        format_name = image_to_save.format or extension.upper()
        save_kwargs = {} if extension.lower() != "jpg" else {"quality": 90}
        image_to_save.save(buffer, format=format_name, **save_kwargs)
        full_path.write_bytes(buffer.getvalue())

        return StorageResult(path=full_path, relative_path=Path(file_name), content_type=content_type)

    def _load_image(self, data: bytes) -> Image.Image:
        try:
            image = Image.open(BytesIO(data))
            image.load()
            return image
        except Exception as exc:  # pragma: no cover - Pillow 예외 메시지 위임
            raise StorageError("이미지 파일을 열 수 없습니다.") from exc

    def _validate_size(self, size: int) -> None:
        if size > self.max_file_size:
            raise StorageError("파일 크기가 제한을 초과했습니다.")

    def _validate_extension(self, extension: str) -> None:
        if extension.lower() not in self.allowed_extensions:
            raise StorageError("지원하지 않는 이미지 확장자입니다.")

    def _resolve_extension(self, filename: str | None, image: Image.Image) -> str:
        if filename:
            ext = Path(filename).suffix.lower().lstrip(".")
            if not ext:
                raise StorageError("파일 확장자를 확인할 수 없습니다.")
            return ext

        if image.format:
            return image.format.lower()

        raise StorageError("파일 확장자를 확인할 수 없습니다.")

    @staticmethod
    def _guess_content_type(extension: str) -> str:
        mapping = {
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "png": "image/png",
            "webp": "image/webp",
        }
        return mapping.get(extension.lower(), "application/octet-stream")
