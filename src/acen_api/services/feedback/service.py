"""피드백/추천 도메인 서비스."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from sqlalchemy.orm import Session

from ...repositories import (
    CalendarRepository,
    DateRepository,
    FeedbackRepository,
    ProductRepository,
    SuggestRepository,
)
from ...schemas import EvaluatorMetrics, SuggestCreate
from ..evaluator.service import EvaluatorService
from .rules import FeedbackPlan, FeedbackRuleEngine, SuggestionHint


@dataclass(slots=True)
class FeedbackResult:
    """생성된 피드백 및 추천 결과."""

    metrics: EvaluatorMetrics
    feedback_id: int
    suggestion_ids: list[int]


class FeedbackService:
    """평가 지표를 기반으로 피드백 및 제품 추천을 생성."""

    def __init__(
        self,
        session: Session,
        rule_engine: FeedbackRuleEngine | None = None,
    ) -> None:
        self.session = session
        self.rule_engine = rule_engine or FeedbackRuleEngine()
        self.evaluator = EvaluatorService(session)
        self.date_repo = DateRepository(session)
        self.feedback_repo = FeedbackRepository(session)
        self.suggest_repo = SuggestRepository(session)
        self.product_repo = ProductRepository(session)
        self.calendar_repo = CalendarRepository(session)

    def generate_for_range(
        self, calendar_id: int, start: date, end: date, *, user_id: int
    ) -> FeedbackResult | None:
        calendar = self.calendar_repo.get(calendar_id)
        if not calendar or calendar.user_id != user_id:
            return None

        dates = self.date_repo.list_by_range(calendar_id, start, end, user_id=user_id)
        if not dates:
            return None

        target_date = dates[-1]
        metrics = self.evaluator.evaluate_range(calendar_id, start, end, user_id=user_id)
        plan = self.rule_engine.build_plan(metrics, target_date.id)

        feedback = self.feedback_repo.create(plan.feedback)
        suggestions = self._persist_suggestions(feedback.id, plan.suggestions)

        return FeedbackResult(
            metrics=metrics,
            feedback_id=feedback.id,
            suggestion_ids=[suggestion.id for suggestion in suggestions],
        )

    def _persist_suggestions(
        self, feedback_id: int, hints: list[SuggestionHint]
    ) -> list:
        created = []
        for hint in hints:
            product = self._select_product_by_tag(hint.tag)
            if not product:
                continue

            suggestion = self.suggest_repo.create(
                SuggestCreate(
                    feedback_id=feedback_id,
                    product_id=product.id,
                    reason=hint.reason,
                    score=hint.score,
                )
            )
            created.append(suggestion)

        return created

    def _select_product_by_tag(self, tag: str):
        candidates = self.product_repo.search_by_tag(tag)
        return candidates[0] if candidates else None
