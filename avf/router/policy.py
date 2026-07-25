"""Pure eligibility and ordering rules for provider selection."""

from dataclasses import dataclass

from avf.capabilities.registry import ProviderDescriptor
from avf.capabilities.requests import CapabilityRequest
from avf.capabilities.types import QualityTier
from avf.router.exceptions import InvalidProviderCostError

_QUALITY_RANK = {
    QualityTier.DRAFT: 0,
    QualityTier.STANDARD: 1,
    QualityTier.HIGH: 2,
    QualityTier.PREMIUM: 3,
}


@dataclass(frozen=True)
class RouterPolicy:
    """Filter and rank declared providers for a capability request."""

    free_first: bool = True

    def is_eligible(
        self,
        descriptor: ProviderDescriptor,
        request: CapabilityRequest,
    ) -> bool:
        if descriptor.provider_id in request.excluded_providers:
            return False
        if _QUALITY_RANK[descriptor.quality_tier] < _QUALITY_RANK[
            request.quality_tier
        ]:
            return False
        if request.max_cost is None:
            return True

        estimated_cost = self.estimated_cost(descriptor)
        return (
            estimated_cost is not None
            and estimated_cost <= request.max_cost
        )

    def selection_key(
        self,
        descriptor: ProviderDescriptor,
        request: CapabilityRequest,
    ) -> tuple[int, int, int, str]:
        preferred = {
            provider_id: index
            for index, provider_id in enumerate(request.preferred_providers)
        }
        preferred_rank = preferred.get(
            descriptor.provider_id,
            len(preferred),
        )
        free_rank = (
            0
            if self.free_first and descriptor.supports_free_tier
            else 1
        )
        return (
            preferred_rank,
            free_rank,
            descriptor.priority,
            descriptor.provider_id,
        )

    @staticmethod
    def estimated_cost(
        descriptor: ProviderDescriptor,
    ) -> float | None:
        if descriptor.supports_free_tier:
            return 0

        value = descriptor.metadata.get("estimated_cost")
        if value is None:
            return None
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise InvalidProviderCostError(
                f"Invalid estimated_cost for provider "
                f"{descriptor.provider_id}: {value!r}"
            )
        if value < 0:
            raise InvalidProviderCostError(
                f"Invalid estimated_cost for provider "
                f"{descriptor.provider_id}: {value!r}"
            )
        return float(value)
