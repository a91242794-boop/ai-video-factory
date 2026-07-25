"""Deterministic quality decisions over capability results."""

from dataclasses import dataclass

from avf.capabilities.results import CapabilityResult
from avf.intelligence.scoring import QualityScore


@dataclass(frozen=True)
class QualityDecision:
    accepted: bool
    score: QualityScore | None
    minimum_score: QualityScore
    reason: str


class QualityGate:
    def evaluate(
        self,
        result: CapabilityResult,
        minimum_score: float,
    ) -> QualityDecision:
        minimum = QualityScore(minimum_score)
        raw_score = result.metrics.quality_score
        if raw_score is None:
            return QualityDecision(
                accepted=True,
                score=None,
                minimum_score=minimum,
                reason="quality score unavailable; accepted for compatibility",
            )

        score = QualityScore(raw_score)
        if score.value >= minimum.value:
            return QualityDecision(
                accepted=True,
                score=score,
                minimum_score=minimum,
                reason="quality threshold met",
            )
        return QualityDecision(
            accepted=False,
            score=score,
            minimum_score=minimum,
            reason=(
                f"QualityRejected: score {score.value} is below "
                f"minimum {minimum.value}"
            ),
        )
