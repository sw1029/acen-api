"""피드백 규칙 정의."""

from __future__ import annotations

from dataclasses import dataclass

from ...schemas import EvaluatorMetrics, FeedbackCreate


@dataclass(slots=True)
class SuggestionHint:
    """추천에 필요한 힌트 정보."""

    tag: str
    reason: str
    score: float


@dataclass(slots=True)
class FeedbackPlan:
    """생성할 피드백과 추천 정보를 담는 컨테이너."""

    feedback: FeedbackCreate
    suggestions: list[SuggestionHint]


class FeedbackRuleEngine:
    """평가 지표를 기반으로 간단한 규칙형 피드백 생성."""

    def __init__(self, adherence_threshold: float = 0.6) -> None:
        self.adherence_threshold = adherence_threshold

    def build_plan(self, metrics: EvaluatorMetrics, date_id: int) -> FeedbackPlan:
        messages: list[str] = []
        category = "maintain"
        severity_score = metrics.severity.current if metrics.severity.current is not None else 0.0

        if metrics.adherence.current < self.adherence_threshold:
            messages.append("일정 수행률이 낮습니다. 루틴 수행 빈도를 높여보세요.")
            category = "routine"
        elif metrics.trend.change and metrics.trend.change > 0:
            messages.append("모델 감지 결과가 증가 추세입니다. 피부 상태 변화를 점검하세요.")
            category = "attention"
        else:
            messages.append("꾸준히 관리가 되고 있습니다. 현재 루틴을 유지하세요.")

        summary = " ".join(messages)
        feedback = FeedbackCreate(
            date_id=date_id,
            title="스킨케어 피드백",
            summary=summary,
            category=category,
            severity_score=severity_score,
        )

        suggestions = self._build_suggestions(metrics, category)
        return FeedbackPlan(feedback=feedback, suggestions=suggestions)

    def _build_suggestions(self, metrics: EvaluatorMetrics, category: str) -> list[SuggestionHint]:
        hints: list[SuggestionHint] = []

        if category == "routine":
            hints.append(
                SuggestionHint(
                    tag="진정",
                    reason="루틴 수행률 개선을 위한 진정 제품을 활용해보세요.",
                    score=0.8,
                )
            )
        elif category == "attention":
            hints.append(
                SuggestionHint(
                    tag="보습",
                    reason="피부 상태 점검과 함께 보습 제품을 강화하세요.",
                    score=0.7,
                )
            )
        else:
            hints.append(
                SuggestionHint(
                    tag="유지",
                    reason="현재 제품 구성을 유지하며 추세를 모니터링하세요.",
                    score=0.6,
                )
            )

        return hints
