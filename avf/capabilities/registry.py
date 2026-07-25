"""In-memory declarations of providers available for each capability."""

from dataclasses import dataclass, field

from avf.capabilities.errors import CapabilityError
from avf.capabilities.types import (
    CapabilityType,
    CostTier,
    QualityTier,
    SpeedTier,
)


@dataclass(frozen=True, kw_only=True)
class ProviderDescriptor:
    """Provider metadata only; it does not hold or create an adapter."""

    provider_id: str
    capability: CapabilityType
    cost_tier: CostTier
    quality_tier: QualityTier
    speed_tier: SpeedTier
    enabled: bool = True
    priority: int = 100
    supports_free_tier: bool = False
    metadata: dict[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.provider_id.strip():
            raise CapabilityError("provider_id must be a non-empty string")
        object.__setattr__(self, "metadata", dict(self.metadata))


class CapabilityRegistry:
    """Register and query provider declarations without loading adapters."""

    def __init__(self) -> None:
        self._providers: dict[str, ProviderDescriptor] = {}

    def register(self, descriptor: ProviderDescriptor) -> None:
        if descriptor.provider_id in self._providers:
            raise CapabilityError(
                f"Provider already registered: {descriptor.provider_id}"
            )
        self._providers[descriptor.provider_id] = descriptor

    def get(self, provider_id: str) -> ProviderDescriptor:
        try:
            return self._providers[provider_id]
        except KeyError as exc:
            raise KeyError(f"Unknown provider: {provider_id}") from exc

    def list_for(
        self,
        capability: CapabilityType,
        enabled_only: bool = True,
    ) -> list[ProviderDescriptor]:
        matches = (
            descriptor
            for descriptor in self._providers.values()
            if descriptor.capability is capability
            and (descriptor.enabled or not enabled_only)
        )
        return sorted(
            matches,
            key=lambda descriptor: (
                descriptor.priority,
                descriptor.provider_id,
            ),
        )

    def clear(self) -> None:
        self._providers.clear()

    def __len__(self) -> int:
        return len(self._providers)
