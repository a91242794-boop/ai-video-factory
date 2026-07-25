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
from avf.intelligence import QualityGate, QualityScore
from avf.resilience import RetryPolicy
from avf.router import ProviderRouter


def _result(score: float | None) -> CapabilityResult:
    return CapabilityResult(
        capability=CapabilityType.IMAGE_GENERATION,
        provider="provider",
        success=True,
        metrics=RunMetrics(quality_score=score),
    )


def test_quality_score_is_immutable_and_limited_to_zero_to_one_hundred() -> None:
    score = QualityScore(75)

    assert score.value == 75
    with pytest.raises(AttributeError):
        score.value = 80  # type: ignore[misc]
    with pytest.raises(ValueError, match="between 0 and 100"):
        QualityScore(101)


def test_quality_gate_accepts_score_at_threshold() -> None:
    decision = QualityGate().evaluate(_result(80), minimum_score=80)

    assert decision.accepted is True
    assert decision.score == QualityScore(80)
    assert decision.minimum_score == QualityScore(80)
    assert decision.reason == "quality threshold met"


def test_quality_gate_rejects_score_below_threshold() -> None:
    decision = QualityGate().evaluate(_result(79), minimum_score=80)

    assert decision.accepted is False
    assert decision.reason.startswith("QualityRejected:")


def test_quality_gate_accepts_missing_score_for_compatibility() -> None:
    decision = QualityGate().evaluate(_result(None), minimum_score=80)

    assert decision.accepted is True
    assert decision.score is None
    assert "compatibility" in decision.reason


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


@dataclass
class _ScoredAdapter:
    provider_id: str
    quality_score: float
    capability: CapabilityType = CapabilityType.IMAGE_GENERATION
    calls: int = 0

    def execute(self, request: CapabilityRequest) -> CapabilityResult:
        self.calls += 1
        return CapabilityResult(
            capability=request.capability,
            provider=self.provider_id,
            success=True,
            metrics=RunMetrics(quality_score=self.quality_score),
        )


def test_execution_falls_back_on_low_quality_without_retrying_provider() -> None:
    providers = CapabilityRegistry()
    providers.register(_provider("draft", 1))
    providers.register(_provider("quality", 2))
    draft = _ScoredAdapter("draft", 60)
    quality = _ScoredAdapter("quality", 90)
    adapters = AdapterRegistry()
    adapters.register(draft)
    adapters.register(quality)
    service = ExecutionService(
        ProviderRouter(providers),
        adapters,
        retry_policy=RetryPolicy(max_retries=3),
    )
    request = CapabilityRequest(
        capability=CapabilityType.IMAGE_GENERATION,
        project_id="mini",
        metadata={"minimum_quality_score": 80},
    )
    context = ExecutionContext(request_id="quality-fallback")

    result = service.execute(request, context)

    assert result.provider == "quality"
    assert draft.calls == 1
    assert quality.calls == 1
    assert context.trace[-1]["fallback_path"] == ["draft", "quality"]
    assert any(
        event["event"] == "quality_rejected"
        and event["provider"] == "draft"
        for event in context.trace
    )
