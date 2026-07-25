import pytest

from avf.adapters.registry import AdapterRegistry
from avf.adapters.stub.image_stub import ImageStubAdapter
from avf.capabilities.registry import CapabilityRegistry, ProviderDescriptor
from avf.capabilities.requests import ImageGenerationRequest
from avf.capabilities.types import (
    CapabilityType,
    CostTier,
    QualityTier,
    SpeedTier,
)
from avf.execution import (
    ExecutionAdapterNotFoundError,
    ExecutionBudgetExceededError,
    ExecutionContext,
    ExecutionProviderNotFoundError,
    ExecutionService,
)
from avf.router.router import ProviderRouter


def _descriptor(
    *,
    provider_id: str = "stub-image",
    estimated_cost: float = 0,
    supports_free_tier: bool = True,
) -> ProviderDescriptor:
    return ProviderDescriptor(
        provider_id=provider_id,
        capability=CapabilityType.IMAGE_GENERATION,
        cost_tier=CostTier.FREE if supports_free_tier else CostTier.LOW,
        quality_tier=QualityTier.STANDARD,
        speed_tier=SpeedTier.FAST,
        supports_free_tier=supports_free_tier,
        metadata={"estimated_cost": estimated_cost},
    )


def _request() -> ImageGenerationRequest:
    return ImageGenerationRequest(
        project_id="mini",
        storyboard={"shots": []},
    )


def _service(
    *,
    descriptor: ProviderDescriptor | None = None,
    with_adapter: bool = True,
) -> ExecutionService:
    providers = CapabilityRegistry()
    if descriptor is not None:
        providers.register(descriptor)
    adapters = AdapterRegistry()
    if with_adapter:
        adapters.register(ImageStubAdapter())
    return ExecutionService(ProviderRouter(providers), adapters)


def test_execute_completes_router_adapter_result_loop() -> None:
    context = ExecutionContext(request_id="req-1")

    result = _service(descriptor=_descriptor()).execute(_request(), context)

    assert result.success is True
    assert result.provider == "stub-image"
    assert result.capability is CapabilityType.IMAGE_GENERATION


def test_execute_raises_clear_error_when_provider_is_missing() -> None:
    with pytest.raises(
        ExecutionProviderNotFoundError,
        match="image_generation",
    ):
        _service().execute(_request(), ExecutionContext(request_id="req-2"))


def test_execute_raises_clear_error_when_adapter_is_missing() -> None:
    with pytest.raises(
        ExecutionAdapterNotFoundError,
        match="stub-image",
    ):
        _service(
            descriptor=_descriptor(),
            with_adapter=False,
        ).execute(_request(), ExecutionContext(request_id="req-3"))


def test_context_budget_limits_provider_selection() -> None:
    paid = _descriptor(
        provider_id="paid-image",
        estimated_cost=1.0,
        supports_free_tier=False,
    )

    with pytest.raises(
        ExecutionBudgetExceededError,
        match="0.5",
    ):
        _service(
            descriptor=paid,
            with_adapter=False,
        ).execute(
            _request(),
            ExecutionContext(request_id="req-4", budget_limit=0.5),
        )


def test_execute_appends_execution_metrics_to_trace() -> None:
    context = ExecutionContext(request_id="req-5")

    _service(descriptor=_descriptor()).execute(_request(), context)

    metrics = context.trace[-1]["metrics"]
    assert metrics["estimated_cost"] == 0
    assert metrics["actual_cost"] == 0
    assert metrics["tokens"] == 0
    assert metrics["duration"] >= 0
    assert metrics["provider_id"] == "stub-image"
    assert metrics["adapter_id"] == "stub-image"


def test_execution_context_trace_is_not_shared() -> None:
    first = ExecutionContext(request_id="req-a")
    second = ExecutionContext(request_id="req-b")

    first.trace.append({"event": "test"})

    assert second.trace == []
