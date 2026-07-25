import pytest

from avf.capabilities.registry import ProviderDescriptor
from avf.capabilities.types import (
    CapabilityType,
    CostTier,
    QualityTier,
    SpeedTier,
)
from avf.resilience import BudgetExceeded, CostGuard


def _provider(*, free: bool, estimated_cost: float | None) -> ProviderDescriptor:
    metadata = (
        {}
        if estimated_cost is None
        else {"estimated_cost": estimated_cost}
    )
    return ProviderDescriptor(
        provider_id="provider",
        capability=CapabilityType.IMAGE_GENERATION,
        cost_tier=CostTier.FREE if free else CostTier.LOW,
        quality_tier=QualityTier.STANDARD,
        speed_tier=SpeedTier.BALANCED,
        supports_free_tier=free,
        metadata=metadata,
    )


def test_cost_guard_allows_provider_within_budget() -> None:
    assert CostGuard().check(
        _provider(free=False, estimated_cost=0.4),
        budget_limit=0.5,
    ) == 0.4


def test_cost_guard_always_allows_free_provider_at_zero_cost() -> None:
    assert CostGuard().check(
        _provider(free=True, estimated_cost=None),
        budget_limit=0,
    ) == 0


@pytest.mark.parametrize("estimated_cost", [0.6, None])
def test_cost_guard_blocks_paid_provider_outside_known_budget(
    estimated_cost: float | None,
) -> None:
    with pytest.raises(BudgetExceeded, match="provider"):
        CostGuard().check(
            _provider(free=False, estimated_cost=estimated_cost),
            budget_limit=0.5,
        )
