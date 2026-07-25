"""Provider performance snapshots and incremental statistics."""

import json
import os
import tempfile
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

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


PerformanceSnapshot = tuple[ProviderPerformance, int]


class PerformanceStorage(ABC):
    """Persistence boundary for provider performance snapshots."""

    @abstractmethod
    def save(self, records: Iterable[PerformanceSnapshot]) -> None:
        """Persist a complete performance snapshot."""

    @abstractmethod
    def load(self) -> list[PerformanceSnapshot]:
        """Load all persisted performance snapshots."""

    @abstractmethod
    def clear(self) -> None:
        """Remove all persisted performance snapshots."""


class JsonPerformanceStorage(PerformanceStorage):
    """Store provider performance snapshots in a versioned JSON file."""

    VERSION = 1

    def __init__(
        self,
        path: str | os.PathLike[str] = "provider_performance.json",
    ) -> None:
        self.path = Path(path)

    def save(self, records: Iterable[PerformanceSnapshot]) -> None:
        payload = {
            "version": self.VERSION,
            "records": [
                {
                    **{
                        field: getattr(performance, field)
                        for field in performance.__dataclass_fields__
                    },
                    "quality_count": quality_count,
                }
                for performance, quality_count in records
            ],
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                "w",
                encoding="utf-8",
                dir=self.path.parent,
                prefix=f".{self.path.name}.",
                suffix=".tmp",
                delete=False,
            ) as temporary_file:
                temporary_path = Path(temporary_file.name)
                json.dump(payload, temporary_file, indent=2)
                temporary_file.write("\n")
                temporary_file.flush()
                os.fsync(temporary_file.fileno())
            os.replace(temporary_path, self.path)
        except BaseException:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)
            raise

    def load(self) -> list[PerformanceSnapshot]:
        if not self.path.exists() or self.path.stat().st_size == 0:
            return []
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        if payload.get("version") != self.VERSION:
            raise ValueError(
                f"Unsupported provider performance version: "
                f"{payload.get('version')!r}"
            )
        snapshots = []
        for record in payload["records"]:
            values = dict(record)
            quality_count = values.pop("quality_count", 0)
            snapshots.append((ProviderPerformance(**values), quality_count))
        return snapshots

    def clear(self) -> None:
        self.path.unlink(missing_ok=True)


class ProviderPerformanceStore:
    """Record provider outcomes, optionally backed by persistent storage."""

    def __init__(self, storage: PerformanceStorage | None = None) -> None:
        self._storage = storage
        self._performance: dict[str, ProviderPerformance] = {}
        self._quality_counts: dict[str, int] = {}
        if storage is not None:
            for performance, quality_count in storage.load():
                self._performance[performance.provider_id] = performance
                self._quality_counts[performance.provider_id] = quality_count

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
        self._save()
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
        if self._storage is not None:
            self._storage.clear()

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

    def _save(self) -> None:
        if self._storage is not None:
            self._storage.save(
                (
                    performance,
                    self._quality_counts[provider_id],
                )
                for provider_id, performance in self._performance.items()
            )
