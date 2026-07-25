"""Provider-neutral quality and cost optimization scoring."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

from avf.capabilities.registry import ProviderDescriptor
from avf.intelligence.scoring import QualityScore

if TYPE_CHECKING:
    from avf.router.ranking import ProviderRanking


@dataclass(frozen=True)
class OptimizationScore:
    provider_id: str
    quality_score: QualityScore
    estimated_cost: float
    composite_score: float


@dataclass(frozen=True)
class Optimizer:
    cost_penalty: float = 4
    quality_weight: float = 0.5
    cost_weight: float = 0.3
    reliability_weight: float = 0.2

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

    def rank_provider(
        self,
        provider: ProviderDescriptor,
    ) -> "ProviderRanking":
        from avf.router.ranking import ProviderRanking

        quality = QualityScore(provider.metadata["quality_score"])
        reliability = provider.metadata["reliability"]
        if isinstance(reliability, bool) or not isinstance(
            reliability,
            (int, float),
        ):
            raise ValueError("reliability must be a number")

        if provider.supports_free_tier:
            estimated_cost = 0.0
        else:
            raw_cost = provider.metadata.get("estimated_cost")
            if isinstance(raw_cost, bool) or not isinstance(
                raw_cost,
                (int, float),
            ):
                raise ValueError(
                    f"Provider {provider.provider_id} requires estimated_cost"
                )
            estimated_cost = float(raw_cost)
            if estimated_cost < 0:
                raise ValueError(
                    "estimated_cost must be zero or greater"
                )

        cost_score = max(0, 1 - min(estimated_cost, 1)) * 100
        ranking_score = (
            quality.value * self.quality_weight
            + cost_score * self.cost_weight
            + float(reliability) * 100 * self.reliability_weight
        )
        return ProviderRanking(
            provider_id=provider.provider_id,
            quality_score=quality,
            reliability=float(reliability),
            estimated_cost=estimated_cost,
            ranking_score=ranking_score,
        )
