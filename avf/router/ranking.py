"""Immutable provider ranking output."""

from dataclasses import dataclass

from avf.intelligence.scoring import QualityScore


@dataclass(frozen=True)
class ProviderRanking:
    provider_id: str
    quality_score: QualityScore
    reliability: float
    estimated_cost: float
    ranking_score: float

    def __post_init__(self) -> None:
        if not self.provider_id.strip():
            raise ValueError("provider_id must be a non-empty string")
        if not 0 <= self.reliability <= 1:
            raise ValueError("reliability must be between 0 and 1")
        if self.estimated_cost < 0:
            raise ValueError("estimated_cost must be zero or greater")
