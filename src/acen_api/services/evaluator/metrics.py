"""평가지표 계산 유틸."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Iterable

from ...schemas import EvaluatorMetrics, MetricBreakdown


@dataclass(slots=True)
class DailyRecord:
    """평가에 필요한 최소 데이터."""

    scheduled_date: date
    completion_ratio: float
    model_count: int
    severity_score: float | None


def compute_metrics(records: Iterable[DailyRecord]) -> EvaluatorMetrics:
    """주어진 기록을 바탕으로 주요 지표를 계산."""

    records = sorted(records, key=lambda item: item.scheduled_date)
    if not records:
        empty = MetricBreakdown(current=0.0, previous=None, change=None)
        return EvaluatorMetrics(adherence=empty, severity=empty, trend=empty, notes="데이터가 없습니다.")

    adherence = _calc_adherence(records)
    severity = _calc_severity(records)
    trend = _calc_trend(records)

    return EvaluatorMetrics(
        adherence=adherence,
        severity=severity,
        trend=trend,
        notes=None,
    )


def _calc_adherence(records: list[DailyRecord]) -> MetricBreakdown:
    current = records[-1].completion_ratio
    previous = records[-2].completion_ratio if len(records) > 1 else None
    change = _change_percentage(previous, current)
    return MetricBreakdown(current=current, previous=previous, change=change)


def _calc_severity(records: list[DailyRecord]) -> MetricBreakdown:
    scored = [r.severity_score for r in records if r.severity_score is not None]
    if not scored:
        return MetricBreakdown(current=0.0, previous=None, change=None)

    current = scored[-1]
    previous = scored[-2] if len(scored) > 1 else None
    change = _change_percentage(previous, current)
    return MetricBreakdown(current=current, previous=previous, change=change)


def _calc_trend(records: list[DailyRecord]) -> MetricBreakdown:
    window = records[-7:]
    if not window:
        return MetricBreakdown(current=0.0, previous=None, change=None)

    current = sum(item.model_count for item in window) / len(window)
    previous_window = records[-14:-7]
    previous = (
        sum(item.model_count for item in previous_window) / len(previous_window)
        if previous_window
        else None
    )
    change = _change_percentage(previous, current)
    return MetricBreakdown(current=current, previous=previous, change=change)


def _change_percentage(previous: float | None, current: float) -> float | None:
    if previous is None or previous == 0:
        return None
    return (current - previous) / previous
