"""Map normalized capability results into provider performance history."""

from avf.capabilities.results import CapabilityResult
from avf.intelligence.performance import (
    ProviderPerformance,
    ProviderPerformanceStore,
)


class MetricsRecorder:
    def __init__(self, store: ProviderPerformanceStore) -> None:
        self._store = store

    def record(
        self,
        result: CapabilityResult,
    ) -> ProviderPerformance:
        return self._store.record_run(
            provider_id=result.provider,
            success=result.success,
            latency=result.metrics.duration_seconds,
            cost=result.metrics.actual_cost,
            quality_score=result.metrics.quality_score,
        )
