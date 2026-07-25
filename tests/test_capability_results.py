import pytest

from avf.capabilities.results import CapabilityResult, RunMetrics
from avf.capabilities.types import CapabilityType


def test_run_metrics_have_zero_cost_and_usage_defaults() -> None:
    metrics = RunMetrics()

    assert metrics.estimated_cost == 0
    assert metrics.actual_cost == 0
    assert metrics.duration_seconds == 0
    assert metrics.quality_score is None
    assert metrics.fallback_count == 0
    assert metrics.model_tokens_used == 0
    assert metrics.cache_hit is False


@pytest.mark.parametrize(
    ("values", "message"),
    [
        ({"estimated_cost": -1}, "estimated_cost must be zero or greater"),
        ({"actual_cost": -1}, "actual_cost must be zero or greater"),
        ({"duration_seconds": -1}, "duration_seconds must be zero or greater"),
        ({"quality_score": -1}, "quality_score must be between 0 and 100"),
        ({"quality_score": 101}, "quality_score must be between 0 and 100"),
        ({"fallback_count": -1}, "fallback_count must be zero or greater"),
        (
            {"model_tokens_used": -1},
            "model_tokens_used must be zero or greater",
        ),
    ],
)
def test_run_metrics_reject_invalid_values(
    values: dict[str, object],
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        RunMetrics(**values)


def test_capability_result_serializes_to_stable_provider_neutral_dict() -> None:
    result = CapabilityResult(
        capability=CapabilityType.IMAGE_GENERATION,
        provider="example-provider",
        success=True,
        output={"z": "last", "a": "first"},
        metrics=RunMetrics(quality_score=92, cache_hit=True),
    )

    assert result.to_dict() == result.to_dict()
    assert result.to_dict() == {
        "capability": "image_generation",
        "provider": "example-provider",
        "success": True,
        "output": {"a": "first", "z": "last"},
        "issues": [],
        "metrics": {
            "estimated_cost": 0,
            "actual_cost": 0,
            "duration_seconds": 0,
            "quality_score": 92,
            "fallback_count": 0,
            "model_tokens_used": 0,
            "cache_hit": True,
        },
    }


def test_result_issues_and_metrics_do_not_share_mutable_defaults() -> None:
    first = CapabilityResult(
        capability=CapabilityType.DIRECTOR,
        provider="first",
        success=False,
    )
    second = CapabilityResult(
        capability=CapabilityType.DIRECTOR,
        provider="second",
        success=False,
    )

    first.issues.append("failed")

    assert second.issues == []
    assert first.metrics is not second.metrics
