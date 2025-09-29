"""평가 결과 스키마."""

from __future__ import annotations

from typing import Annotated

from pydantic import Field

from .base import APIModel


class MetricBreakdown(APIModel):
    """세부 지표를 표현."""

    current: Annotated[float, Field(ge=0, le=1)]
    previous: Annotated[float | None, Field(None, ge=0, le=1)] = None
    change: float | None = None


class EvaluatorMetrics(APIModel):
    """평가지표 묶음."""

    adherence: MetricBreakdown
    severity: MetricBreakdown
    trend: MetricBreakdown
    notes: str | None = None
