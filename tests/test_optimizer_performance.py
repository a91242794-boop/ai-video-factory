from avf.capabilities.registry import CapabilityRegistry, ProviderDescriptor
from avf.capabilities.requests import CapabilityRequest
from avf.capabilities.types import (
    CapabilityType,
    CostTier,
    QualityTier,
    SpeedTier,
)
from avf.intelligence import Optimizer
from avf.intelligence.performance import ProviderPerformanceStore
from avf.router import ProviderRouter


def _provider(
    provider_id: str,
    *,
    priority: int,
    quality_score: float,
    reliability: float,
    estimated_cost: float,
) -> ProviderDescriptor:
    return ProviderDescriptor(
        provider_id=provider_id,
        capability=CapabilityType.IMAGE_GENERATION,
        cost_tier=CostTier.LOW,
        quality_tier=QualityTier.STANDARD,
        speed_tier=SpeedTier.BALANCED,
        priority=priority,
        metadata={
            "quality_score": quality_score,
            "reliability": reliability,
            "estimated_cost": estimated_cost,
        },
    )


def _record(
    store: ProviderPerformanceStore,
    provider_id: str,
    *,
    success: bool,
    quality_score: float,
    cost: float,
) -> None:
    store.record_run(
        provider_id=provider_id,
        success=success,
        latency=1,
        cost=cost,
        quality_score=quality_score,
    )


def test_optimizer_prefers_historical_performance_over_metadata() -> None:
    store = ProviderPerformanceStore()
    _record(
        store,
        "provider",
        success=True,
        quality_score=90,
        cost=0.1,
    )
    provider = _provider(
        "provider",
        priority=1,
        quality_score=20,
        reliability=0.1,
        estimated_cost=0.9,
    )

    ranking = Optimizer(performance_store=store).rank_provider(provider)

    assert ranking.quality_score.value == 90
    assert ranking.estimated_cost == 0.1
    assert ranking.reliability == 1
    assert ranking.ranking_score == 92


def test_optimizer_falls_back_to_metadata_without_history() -> None:
    provider = _provider(
        "provider",
        priority=1,
        quality_score=80,
        reliability=0.9,
        estimated_cost=0.1,
    )

    ranking = Optimizer(
        performance_store=ProviderPerformanceStore()
    ).rank_provider(provider)

    assert ranking.ranking_score == 85


def test_router_candidates_use_store_but_select_keeps_legacy_order() -> None:
    store = ProviderPerformanceStore()
    _record(
        store,
        "legacy-first",
        success=False,
        quality_score=50,
        cost=0.5,
    )
    _record(
        store,
        "historical-best",
        success=True,
        quality_score=95,
        cost=0.05,
    )
    registry = CapabilityRegistry()
    registry.register(
        _provider(
            "legacy-first",
            priority=1,
            quality_score=90,
            reliability=1,
            estimated_cost=0,
        )
    )
    registry.register(
        _provider(
            "historical-best",
            priority=2,
            quality_score=10,
            reliability=0,
            estimated_cost=1,
        )
    )
    router = ProviderRouter(
        registry,
        optimizer=Optimizer(performance_store=store),
    )
    request = CapabilityRequest(
        capability=CapabilityType.IMAGE_GENERATION,
        project_id="mini",
    )

    assert router.select(request).provider_id == "legacy-first"
    assert [
        item.provider_id for item in router.select_candidates(request)
    ] == ["historical-best", "legacy-first"]
