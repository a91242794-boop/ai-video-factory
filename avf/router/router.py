"""Provider selection over the in-memory CapabilityRegistry."""

from avf.capabilities.registry import (
    CapabilityRegistry,
    ProviderDescriptor,
)
from avf.capabilities.requests import CapabilityRequest
from avf.router.exceptions import NoProviderAvailableError
from avf.router.policy import RouterPolicy


class ProviderRouter:
    """Select one eligible provider declaration without executing it."""

    def __init__(
        self,
        registry: CapabilityRegistry,
        policy: RouterPolicy | None = None,
    ) -> None:
        self._registry = registry
        self._policy = policy or RouterPolicy()

    def select(
        self,
        request: CapabilityRequest,
    ) -> ProviderDescriptor:
        candidates = (
            descriptor
            for descriptor in self._registry.list_for(request.capability)
            if self._policy.is_eligible(descriptor, request)
        )
        ordered = sorted(
            candidates,
            key=lambda descriptor: self._policy.selection_key(
                descriptor,
                request,
            ),
        )
        if not ordered:
            raise NoProviderAvailableError(
                "No eligible provider for capability "
                f"{request.capability.value}"
            )
        return ordered[0]
