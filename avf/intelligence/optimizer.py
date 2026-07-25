"""Provider-neutral quality and cost optimization scoring."""

from dataclasses import dataclass

from avf.intelligence.scoring import QualityScore


@dataclass(frozen=True)
class OptimizationScore:
    provider_id: str
    quality_score: QualityScore
    estimated_cost: float
    composite_score: float


@dataclass(frozen=True)
class Optimizer:
    cost_penalty: float = 4

    def optimize(
        self,
        *,
        quality_score: float,
        estimated_cost: float,
        provider_id: str,
    ) -> OptimizationScore:
        if not provider_id.strip():
            raise ValueError("provider_id must be a non-empty string")
        if estimated_cost < 0:
            raise ValueError("estimated_cost must be zero or greater")

        quality = QualityScore(quality_score)
        composite = max(
            0,
            quality.value - estimated_cost * self.cost_penalty,
        )
        return OptimizationScore(
            provider_id=provider_id,
            quality_score=quality,
            estimated_cost=estimated_cost,
            composite_score=composite,
        )
