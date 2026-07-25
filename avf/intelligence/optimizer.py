"""Provider-neutral quality, cost, and performance optimization."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

from avf.capabilities.registry import ProviderDescriptor
from avf.intelligence.performance import ProviderPerformanceStore
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
    performance_store: ProviderPerformanceStore | None = None

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

    def can_rank_provider(self, provider: ProviderDescriptor) -> bool:
        try:
            self._ranking_inputs(provider)
        except (KeyError, ValueError):
            return False
        return True

    def rank_provider(
        self,
        provider: ProviderDescriptor,
    ) -> "ProviderRanking":
        from avf.router.ranking import ProviderRanking

        quality, reliability, estimated_cost = self._ranking_inputs(
            provider
        )
        cost_score = max(0, 1 - min(estimated_cost, 1)) * 100
        ranking_score = (
            quality.value * self.quality_weight
            + cost_score * self.cost_weight
            + reliability * 100 * self.reliability_weight
        )
        return ProviderRanking(
            provider_id=provider.provider_id,
            quality_score=quality,
            reliability=reliability,
            estimated_cost=estimated_cost,
            ranking_score=ranking_score,
        )

    def _ranking_inputs(
        self,
        provider: ProviderDescriptor,
    ) -> tuple[QualityScore, float, float]:
        performance = None
        if (
            self.performance_store is not None
            and self.performance_store.contains(provider.provider_id)
        ):
            performance = self.performance_store.get(provider.provider_id)

        quality_value = (
            performance.quality_score
            if performance is not None
            and performance.quality_score is not None
            else provider.metadata["quality_score"]
        )
        quality = QualityScore(quality_value)

        if performance is not None:
            return (
                quality,
                performance.success_rate,
                performance.avg_cost,
            )

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
        return quality, float(reliability), estimated_cost
