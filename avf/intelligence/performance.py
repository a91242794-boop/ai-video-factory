"""In-memory provider performance snapshots and incremental statistics."""

from dataclasses import dataclass

from avf.intelligence.scoring import QualityScore


@dataclass(frozen=True)
class ProviderPerformance:
    provider_id: str
    success_rate: float
    avg_latency: float
    avg_cost: float
    quality_score: float | None
    total_runs: int
    failed_runs: int


class ProviderPerformanceStore:
    """Record process-local provider outcomes without external storage."""

    def __init__(self) -> None:
        self._performance: dict[str, ProviderPerformance] = {}
        self._quality_counts: dict[str, int] = {}

    def record_run(
        self,
        *,
        provider_id: str,
        success: bool,
        latency: float,
        cost: float,
        quality_score: float | None,
    ) -> ProviderPerformance:
        if not provider_id.strip():
            raise ValueError("provider_id must be a non-empty string")
        if latency < 0:
            raise ValueError("latency must be zero or greater")
        if cost < 0:
            raise ValueError("cost must be zero or greater")
        if quality_score is not None:
            QualityScore(quality_score)

        previous = self._performance.get(provider_id)
        total_runs = 1 if previous is None else previous.total_runs + 1
        failed_runs = (
            (0 if success else 1)
            if previous is None
            else previous.failed_runs + (0 if success else 1)
        )
        avg_latency = self._average(
            0 if previous is None else previous.avg_latency,
            0 if previous is None else previous.total_runs,
            latency,
        )
        avg_cost = self._average(
            0 if previous is None else previous.avg_cost,
            0 if previous is None else previous.total_runs,
            cost,
        )
        previous_quality_count = self._quality_counts.get(provider_id, 0)
        previous_quality = (
            None if previous is None else previous.quality_score
        )
        if quality_score is None:
            average_quality = previous_quality
            quality_count = previous_quality_count
        else:
            average_quality = self._average(
                0 if previous_quality is None else previous_quality,
                previous_quality_count,
                quality_score,
            )
            quality_count = previous_quality_count + 1

        performance = ProviderPerformance(
            provider_id=provider_id,
            success_rate=(total_runs - failed_runs) / total_runs,
            avg_latency=avg_latency,
            avg_cost=avg_cost,
            quality_score=average_quality,
            total_runs=total_runs,
            failed_runs=failed_runs,
        )
        self._performance[provider_id] = performance
        self._quality_counts[provider_id] = quality_count
        return performance

    def get(self, provider_id: str) -> ProviderPerformance:
        try:
            return self._performance[provider_id]
        except KeyError as error:
            raise KeyError(
                f"Unknown provider performance: {provider_id}"
            ) from error

    def contains(self, provider_id: str) -> bool:
        return provider_id in self._performance

    def clear(self) -> None:
        self._performance.clear()
        self._quality_counts.clear()

    def __len__(self) -> int:
        return len(self._performance)

    @staticmethod
    def _average(
        previous_average: float,
        previous_count: int,
        value: float,
    ) -> float:
        return (
            previous_average * previous_count + value
        ) / (previous_count + 1)
