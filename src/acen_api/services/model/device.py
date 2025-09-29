"""디바이스 선택 유틸."""

from __future__ import annotations

from typing import Literal

try:
    import torch
except ImportError:  # pragma: no cover - torch 미설치 환경
    torch = None  # type: ignore[assignment]

AvailableDevice = Literal["cpu", "cuda"]


def choose_device(preferred: str | None = None) -> AvailableDevice:
    """환경에 맞는 실행 디바이스 선택."""

    if preferred:
        preferred = preferred.lower()
        if preferred == "cuda" and torch and torch.cuda.is_available():
            return "cuda"
        if preferred == "cpu":
            return "cpu"

    if torch and torch.cuda.is_available():
        return "cuda"

    return "cpu"
