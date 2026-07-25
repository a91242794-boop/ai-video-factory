from avf.capabilities.registry import CapabilityRegistry, ProviderDescriptor
from avf.capabilities.requests import CapabilityRequest
from avf.capabilities.types import (
    CapabilityType,
    CostTier,
    QualityTier,
    SpeedTier,
)
from avf.router import ProviderRouter


def _provider(
    provider_id: str,
    *,
    priority: int,
    free: bool = False,
    quality_score: float | None = None,
    reliability: float | None = None,
    estimated_cost: float | None = None,
) -> ProviderDescriptor:
    metadata: dict[str, object] = {}
    if quality_score is not None:
        metadata["quality_score"] = quality_score
    if reliability is not None:
        metadata["reliability"] = reliability
    if estimated_cost is not None:
        metadata["estimated_cost"] = estimated_cost
    return ProviderDescriptor(
        provider_id=provider_id,
        capability=CapabilityType.IMAGE_GENERATION,
        cost_tier=CostTier.FREE if free else CostTier.LOW,
        quality_tier=QualityTier.STANDARD,
        speed_tier=SpeedTier.BALANCED,
        priority=priority,
        supports_free_tier=free,
        metadata=metadata,
    )


def _router(*providers: ProviderDescriptor) -> ProviderRouter:
    registry = CapabilityRegistry()
    for provider in providers:
        registry.register(provider)
    return ProviderRouter(registry)


def _request() -> CapabilityRequest:
    return CapabilityRequest(
        capability=CapabilityType.IMAGE_GENERATION,
        project_id="mini",
    )


def test_select_keeps_legacy_order_when_ranked_metadata_is_complete() -> None:
    router = _router(
        _provider(
            "legacy-first",
            priority=1,
            quality_score=60,
            reliability=0.7,
            estimated_cost=0.5,
        ),
        _provider(
            "optimized-first",
            priority=2,
            quality_score=95,
            reliability=0.99,
            estimated_cost=0.1,
        ),
    )

    assert router.select(_request()).provider_id == "legacy-first"


def test_select_candidates_uses_optimizer_when_all_metadata_is_complete() -> None:
    router = _router(
        _provider(
            "legacy-first",
            priority=1,
            quality_score=60,
            reliability=0.7,
            estimated_cost=0.5,
        ),
        _provider(
            "optimized-first",
            priority=2,
            quality_score=95,
            reliability=0.99,
            estimated_cost=0.1,
        ),
    )

    candidates = router.select_candidates(_request())

    assert [item.provider_id for item in candidates] == [
        "optimized-first",
        "legacy-first",
    ]


def test_select_candidates_uses_legacy_order_when_metadata_is_incomplete() -> None:
    router = _router(
        _provider("paid-priority", priority=1, estimated_cost=0.1),
        _provider("free", priority=50, free=True),
    )

    candidates = router.select_candidates(_request())

    assert [item.provider_id for item in candidates] == [
        "free",
        "paid-priority",
    ]


def test_ranked_candidates_use_provider_id_as_stable_tie_breaker() -> None:
    router = _router(
        _provider(
            "z-provider",
            priority=1,
            quality_score=80,
            reliability=0.9,
            estimated_cost=0.1,
        ),
        _provider(
            "a-provider",
            priority=100,
            quality_score=80,
            reliability=0.9,
            estimated_cost=0.1,
        ),
    )

    assert [
        item.provider_id for item in router.select_candidates(_request())
    ] == ["a-provider", "z-provider"]
