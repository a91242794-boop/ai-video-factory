import pytest

from avf.capabilities.registry import (
    CapabilityRegistry,
    ProviderDescriptor,
)
from avf.capabilities.requests import CapabilityRequest
from avf.capabilities.types import (
    CapabilityType,
    CostTier,
    QualityTier,
    SpeedTier,
)
from avf.router import NoProviderAvailableError, ProviderRouter


def provider(
    provider_id: str,
    *,
    priority: int = 100,
    free: bool = False,
    quality: QualityTier = QualityTier.STANDARD,
    cost: float | None = None,
    enabled: bool = True,
) -> ProviderDescriptor:
    metadata: dict[str, object] = {}
    if cost is not None:
        metadata["estimated_cost"] = cost
    return ProviderDescriptor(
        provider_id=provider_id,
        capability=CapabilityType.IMAGE_GENERATION,
        cost_tier=CostTier.FREE if free else CostTier.PREMIUM,
        quality_tier=quality,
        speed_tier=SpeedTier.BALANCED,
        enabled=enabled,
        priority=priority,
        supports_free_tier=free,
        metadata=metadata,
    )


def request(**overrides: object) -> CapabilityRequest:
    values: dict[str, object] = {
        "capability": CapabilityType.IMAGE_GENERATION,
        "project_id": "mini",
        "quality_tier": QualityTier.STANDARD,
    }
    values.update(overrides)
    return CapabilityRequest(**values)


def router_with(*providers: ProviderDescriptor) -> ProviderRouter:
    registry = CapabilityRegistry()
    for item in providers:
        registry.register(item)
    return ProviderRouter(registry)


def test_free_provider_is_preferred_over_lower_priority_paid_provider() -> None:
    router = router_with(
        provider("paid", priority=1, cost=0.2),
        provider("free", priority=50, free=True),
    )

    assert router.select(request()).provider_id == "free"


def test_premium_provider_is_fallback_when_free_quality_is_too_low() -> None:
    router = router_with(
        provider("free-draft", free=True, quality=QualityTier.DRAFT),
        provider(
            "premium-high",
            quality=QualityTier.HIGH,
            cost=1.0,
        ),
    )

    selected = router.select(request(quality_tier=QualityTier.HIGH))

    assert selected.provider_id == "premium-high"


def test_preferred_provider_wins_when_it_is_eligible() -> None:
    router = router_with(
        provider("free", free=True),
        provider("preferred-paid", cost=0.2),
    )

    selected = router.select(
        request(preferred_providers=("preferred-paid",))
    )

    assert selected.provider_id == "preferred-paid"


def test_excluded_provider_is_never_selected() -> None:
    router = router_with(
        provider("excluded-free", free=True),
        provider("allowed-paid", cost=0.3),
    )

    selected = router.select(
        request(excluded_providers=("excluded-free",))
    )

    assert selected.provider_id == "allowed-paid"


def test_budget_filters_expensive_and_unknown_cost_providers() -> None:
    router = router_with(
        provider("expensive", priority=1, cost=2.0),
        provider("unknown-cost", priority=2),
        provider("affordable", priority=3, cost=0.4),
    )

    selected = router.select(request(max_cost=0.5))

    assert selected.provider_id == "affordable"


def test_stable_ordering_uses_priority_then_provider_id() -> None:
    router = router_with(
        provider("z-provider", priority=10, cost=0.1),
        provider("a-provider", priority=10, cost=0.1),
    )

    assert router.select(request()).provider_id == "a-provider"


def test_no_provider_error_when_all_candidates_are_ineligible() -> None:
    router = router_with(
        provider("disabled", enabled=False),
        provider("low-quality", quality=QualityTier.DRAFT, cost=0.1),
    )

    with pytest.raises(
        NoProviderAvailableError,
        match="No eligible provider for capability image_generation",
    ):
        router.select(request(quality_tier=QualityTier.PREMIUM))
