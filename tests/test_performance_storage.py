import json
import os
from pathlib import Path

import pytest

from avf.intelligence.performance import (
    JsonPerformanceStorage,
    ProviderPerformance,
    ProviderPerformanceStore,
)


def _record() -> ProviderPerformance:
    return ProviderPerformance(
        provider_id="image-a",
        success_rate=0.5,
        avg_latency=3.0,
        avg_cost=0.3,
        quality_score=70.0,
        total_runs=2,
        failed_runs=1,
    )


def test_json_storage_saves_and_loads_records(tmp_path: Path) -> None:
    path = tmp_path / "performance.json"
    storage = JsonPerformanceStorage(path)

    storage.save([(_record(), 2)])

    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["version"] == 1
    assert payload["records"][0]["provider_id"] == "image-a"
    assert storage.load() == [(_record(), 2)]


def test_store_restores_records_after_restart(tmp_path: Path) -> None:
    storage = JsonPerformanceStorage(tmp_path / "performance.json")
    first_store = ProviderPerformanceStore(storage=storage)
    first_store.record_run(
        provider_id="image-a",
        success=True,
        latency=2,
        cost=0.2,
        quality_score=80,
    )

    restored_store = ProviderPerformanceStore(storage=storage)
    performance = restored_store.record_run(
        provider_id="image-a",
        success=False,
        latency=4,
        cost=0.4,
        quality_score=60,
    )

    assert performance.provider_id == "image-a"
    assert performance.success_rate == 0.5
    assert performance.avg_latency == 3
    assert performance.avg_cost == pytest.approx(0.3)
    assert performance.quality_score == 70
    assert performance.total_runs == 2
    assert performance.failed_runs == 1


def test_store_clear_removes_memory_and_persisted_data(
    tmp_path: Path,
) -> None:
    storage = JsonPerformanceStorage(tmp_path / "performance.json")
    store = ProviderPerformanceStore(storage=storage)
    store.record_run(
        provider_id="image-a",
        success=True,
        latency=1,
        cost=0,
        quality_score=None,
    )

    store.clear()

    assert len(store) == 0
    assert storage.load() == []


def test_empty_file_loads_as_empty_storage(tmp_path: Path) -> None:
    path = tmp_path / "performance.json"
    path.touch()

    assert JsonPerformanceStorage(path).load() == []


def test_version_one_is_supported(tmp_path: Path) -> None:
    path = tmp_path / "performance.json"
    path.write_text('{"version": 1, "records": []}', encoding="utf-8")

    assert JsonPerformanceStorage(path).load() == []


def test_unsupported_version_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "performance.json"
    path.write_text('{"version": 2, "records": []}', encoding="utf-8")

    with pytest.raises(ValueError, match="version"):
        JsonPerformanceStorage(path).load()


def test_save_uses_atomic_replace(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    path = tmp_path / "performance.json"
    calls: list[tuple[Path, Path]] = []
    real_replace = os.replace

    def track_replace(source: Path, target: Path) -> None:
        calls.append((source, target))
        real_replace(source, target)

    monkeypatch.setattr(
        "avf.intelligence.performance.os.replace",
        track_replace,
    )

    JsonPerformanceStorage(path).save([(_record(), 2)])

    assert len(calls) == 1
    source, target = calls[0]
    assert source.parent == path.parent
    assert source != path
    assert target == path
    assert not source.exists()


def test_default_storage_path() -> None:
    assert JsonPerformanceStorage().path == Path("provider_performance.json")
