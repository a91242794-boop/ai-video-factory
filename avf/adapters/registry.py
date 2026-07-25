"""In-memory registry of executable adapters."""

from avf.adapters.base import AdapterContract
from avf.capabilities.types import CapabilityType


class AdapterRegistry:
    """Map provider identifiers to already-created adapter instances."""

    def __init__(self) -> None:
        self._adapters: dict[str, AdapterContract] = {}

    def register(self, adapter: AdapterContract) -> None:
        if adapter.provider_id in self._adapters:
            raise ValueError(
                f"Adapter already registered: {adapter.provider_id}"
            )
        self._adapters[adapter.provider_id] = adapter

    def get(self, provider_id: str) -> AdapterContract:
        try:
            return self._adapters[provider_id]
        except KeyError as exc:
            raise KeyError(f"Unknown adapter: {provider_id}") from exc

    def list(
        self,
        capability: CapabilityType | None = None,
    ) -> list[AdapterContract]:
        adapters = (
            adapter
            for adapter in self._adapters.values()
            if capability is None or adapter.capability is capability
        )
        return sorted(adapters, key=lambda adapter: adapter.provider_id)

    def clear(self) -> None:
        self._adapters.clear()
