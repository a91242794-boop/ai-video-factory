from dataclasses import dataclass

import pytest

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
from avf.execution.recorder import MetricsRecorder
from avf.intelligence.performance import ProviderPerformanceStore
from avf.resilience import ProviderUnavailable, RetryPolicy
from avf.router import ProviderRouter


def _provider(provider_id: str, priority: int = 1) -> ProviderDescriptor:
    return ProviderDescriptor(
        provider_id=provider_id,
        capability=CapabilityType.IMAGE_GENERATION,
        cost_tier=CostTier.FREE,
        quality_tier=QualityTier.STANDARD,
        speed_tier=SpeedTier.BALANCED,
        priority=priority,
        supports_free_tier=True,
    )


def _request(minimum_score: float | None = None) -> CapabilityRequest:
    metadata = (
        {}
        if minimum_score is None
        else {"minimum_quality_score": minimum_score}
    )
    return CapabilityRequest(
        capability=CapabilityType.IMAGE_GENERATION,
        project_id="mini",
        metadata=metadata,
    )


def test_metrics_recorder_writes_capability_result_to_store() -> None:
    store = ProviderPerformanceStore()
    recorder = MetricsRecorder(store)
    result = CapabilityResult(
        capability=CapabilityType.IMAGE_GENERATION,
        provider="image-a",
        success=True,
        metrics=RunMetrics(
            actual_cost=0.2,
            duration_seconds=1.5,
            quality_score=88,
        ),
    )

    performance = recorder.record(result)

    assert performance.provider_id == "image-a"
    assert performance.success_rate == 1
    assert performance.avg_latency == 1.5
    assert performance.avg_cost == 0.2
    assert performance.quality_score == 88


@dataclass
class _ResultAdapter:
    provider_id: str
    score: float
    success: bool = True
    capability: CapabilityType = CapabilityType.IMAGE_GENERATION
    calls: int = 0

    def execute(self, request: CapabilityRequest) -> CapabilityResult:
        self.calls += 1
        return CapabilityResult(
            capability=request.capability,
            provider=self.provider_id,
            success=self.success,
            issues=[] if self.success else ["failed"],
            metrics=RunMetrics(actual_cost=0.1, quality_score=self.score),
        )


@dataclass
class _FailingAdapter:
    provider_id: str = "failing"
    capability: CapabilityType = CapabilityType.IMAGE_GENERATION
    calls: int = 0

    def execute(self, request: CapabilityRequest) -> CapabilityResult:
        self.calls += 1
        raise ProviderUnavailable("offline")


def _service(
    adapters_to_register: list[object],
    providers: list[ProviderDescriptor],
    store: ProviderPerformanceStore,
    *,
    max_retries: int = 0,
) -> ExecutionService:
    registry = CapabilityRegistry()
    for provider in providers:
        registry.register(provider)
    adapters = AdapterRegistry()
    for adapter in adapters_to_register:
        adapters.register(adapter)  # type: ignore[arg-type]
    return ExecutionService(
        ProviderRouter(registry),
        adapters,
        retry_policy=RetryPolicy(max_retries=max_retries),
        metrics_recorder=MetricsRecorder(store),
    )


def test_execution_records_successful_adapter_call() -> None:
    store = ProviderPerformanceStore()
    adapter = _ResultAdapter("success", 90)

    result = _service(
        [adapter],
        [_provider("success")],
        store,
    ).execute(_request(), ExecutionContext(request_id="success"))

    assert result.success is True
    performance = store.get("success")
    assert performance.total_runs == 1
    assert performance.failed_runs == 0
    assert performance.avg_latency >= 0
    assert performance.avg_cost == 0.1
    assert performance.quality_score == 90


def test_each_failed_retry_is_recorded_as_a_separate_run() -> None:
    store = ProviderPerformanceStore()
    adapter = _FailingAdapter()
    service = _service(
        [adapter],
        [_provider("failing")],
        store,
        max_retries=1,
    )

    with pytest.raises(ProviderUnavailable, match="offline"):
        service.execute(_request(), ExecutionContext(request_id="failure"))

    performance = store.get("failing")
    assert adapter.calls == 2
    assert performance.total_runs == 2
    assert performance.failed_runs == 2
    assert performance.success_rate == 0


def test_quality_rejection_records_failure_and_preserves_score() -> None:
    store = ProviderPerformanceStore()
    rejected = _ResultAdapter("draft", 60)
    accepted = _ResultAdapter("quality", 90)
    service = _service(
        [rejected, accepted],
        [_provider("draft", 1), _provider("quality", 2)],
        store,
    )

    result = service.execute(
        _request(minimum_score=80),
        ExecutionContext(request_id="quality"),
    )

    assert result.provider == "quality"
    draft_performance = store.get("draft")
    assert draft_performance.failed_runs == 1
    assert draft_performance.quality_score == 60
    quality_performance = store.get("quality")
    assert quality_performance.failed_runs == 0
    assert quality_performance.quality_score == 90
