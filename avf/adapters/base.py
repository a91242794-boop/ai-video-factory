"""Provider adapter protocol and shared local-result helper."""

from typing import Protocol, runtime_checkable

from avf.capabilities.requests import CapabilityRequest
from avf.capabilities.results import CapabilityResult, RunMetrics
from avf.capabilities.types import CapabilityType


@runtime_checkable
class AdapterContract(Protocol):
    """Execute one provider-neutral request for one declared provider."""

    provider_id: str
    capability: CapabilityType

    def execute(
        self,
        request: CapabilityRequest,
    ) -> CapabilityResult:
        """Execute a capability request and return a normalized result."""
        ...


def successful_stub_result(
    *,
    provider_id: str,
    capability: CapabilityType,
    output: dict[str, object],
) -> CapabilityResult:
    """Create a successful local result with explicit zero usage."""
    return CapabilityResult(
        capability=capability,
        provider=provider_id,
        success=True,
        output=output,
        metrics=RunMetrics(
            estimated_cost=0,
            actual_cost=0,
            model_tokens_used=0,
        ),
    )
