import pytest

from avf.intelligence.performance import ProviderPerformanceStore


def test_store_records_incremental_provider_performance() -> None:
    store = ProviderPerformanceStore()

    first = store.record_run(
        provider_id="image-a",
        success=True,
        latency=2,
        cost=0.2,
        quality_score=80,
    )
    performance = store.record_run(
        provider_id="image-a",
        success=False,
        latency=4,
        cost=0.4,
        quality_score=60,
    )

    assert first.total_runs == 1
    assert performance.provider_id == "image-a"
    assert performance.success_rate == 0.5
    assert performance.avg_latency == 3
    assert performance.avg_cost == pytest.approx(0.3)
    assert performance.quality_score == 70
    assert performance.total_runs == 2
    assert performance.failed_runs == 1


def test_missing_quality_does_not_change_quality_average() -> None:
    store = ProviderPerformanceStore()
    store.record_run(
        provider_id="image-a",
        success=True,
        latency=1,
        cost=0,
        quality_score=90,
    )

    performance = store.record_run(
        provider_id="image-a",
        success=True,
        latency=1,
        cost=0,
        quality_score=None,
    )

    assert performance.quality_score == 90


def test_store_supports_get_contains_clear_and_len() -> None:
    store = ProviderPerformanceStore()
    store.record_run(
        provider_id="image-a",
        success=True,
        latency=1,
        cost=0,
        quality_score=None,
    )

    assert store.contains("image-a") is True
    assert store.get("image-a").provider_id == "image-a"
    assert len(store) == 1
    store.clear()
    assert len(store) == 0
    assert store.contains("image-a") is False
    with pytest.raises(KeyError, match="image-a"):
        store.get("image-a")


@pytest.mark.parametrize(
    ("latency", "cost", "quality_score", "message"),
    [
        (-1, 0, 80, "latency"),
        (1, -0.1, 80, "cost"),
        (1, 0, 101, "quality score"),
    ],
)
def test_store_rejects_invalid_run_metrics(
    latency: float,
    cost: float,
    quality_score: float,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        ProviderPerformanceStore().record_run(
            provider_id="image-a",
            success=True,
            latency=latency,
            cost=cost,
            quality_score=quality_score,
        )
