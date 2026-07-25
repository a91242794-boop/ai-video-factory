from dataclasses import dataclass

from avf.adapters.registry import AdapterRegistry
from avf.capabilities.registry import CapabilityRegistry, ProviderDescriptor
from avf.capabilities.requests import CapabilityRequest
from avf.capabilities.results import CapabilityResult, RunMetrics
from avf.capabilities.types import (
    CapabilityType,
    CostTier,
    QualityTier,
    SpeedTier,
)
from avf.execution import ExecutionContext, ExecutionService
from avf.resilience import FallbackPolicy, ProviderUnavailable, RetryPolicy
from avf.router import ProviderRouter


def _provider(provider_id: str, priority: int) -> ProviderDescriptor:
    return ProviderDescriptor(
        provider_id=provider_id,
        capability=CapabilityType.IMAGE_GENERATION,
        cost_tier=CostTier.FREE,
        quality_tier=QualityTier.STANDARD,
        speed_tier=SpeedTier.BALANCED,
        priority=priority,
        supports_free_tier=True,
    )


def _request() -> CapabilityRequest:
    return CapabilityRequest(
        capability=CapabilityType.IMAGE_GENERATION,
        project_id="mini",
    )


@dataclass
class _FailingAdapter:
    provider_id: str = "first"
    capability: CapabilityType = CapabilityType.IMAGE_GENERATION
    calls: int = 0

    def execute(self, request: CapabilityRequest) -> CapabilityResult:
        self.calls += 1
        raise ProviderUnavailable("first is unavailable")


@dataclass
class _SuccessfulAdapter:
    provider_id: str = "second"
    capability: CapabilityType = CapabilityType.IMAGE_GENERATION
    calls: int = 0

    def execute(self, request: CapabilityRequest) -> CapabilityResult:
        self.calls += 1
        return CapabilityResult(
            capability=request.capability,
            provider=self.provider_id,
            success=True,
            output={"provider": self.provider_id},
            metrics=RunMetrics(),
        )


def _router() -> ProviderRouter:
    registry = CapabilityRegistry()
    registry.register(_provider("second", priority=2))
    registry.register(_provider("first", priority=1))
    return ProviderRouter(registry)


def test_router_select_candidates_preserves_selection_order() -> None:
    candidates = _router().select_candidates(_request())

    assert [item.provider_id for item in candidates] == ["first", "second"]
    assert _router().select(_request()).provider_id == "first"


def test_fallback_policy_uses_router_candidate_order() -> None:
    candidates = FallbackPolicy(_router()).candidates(_request())

    assert [item.provider_id for item in candidates] == ["first", "second"]


def test_execution_retries_then_falls_back_and_records_full_trace() -> None:
    failing = _FailingAdapter()
    successful = _SuccessfulAdapter()
    adapters = AdapterRegistry()
    adapters.register(failing)
    adapters.register(successful)
    context = ExecutionContext(request_id="req-fallback", budget_limit=0)
    service = ExecutionService(
        _router(),
        adapters,
        retry_policy=RetryPolicy(max_retries=1),
    )

    result = service.execute(_request(), context)

    assert result.provider == "second"
    assert failing.calls == 2
    assert successful.calls == 1
    completed = context.trace[-1]
    assert completed["request_id"] == "req-fallback"
    assert completed["provider"] == "second"
    assert completed["adapter"] == "second"
    assert completed["retry_count"] == 1
    assert completed["fallback_path"] == ["first", "second"]
    assert completed["cost"] == {
        "estimated": 0,
        "actual": 0,
    }
