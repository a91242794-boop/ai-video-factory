import pytest

from avf.resilience import (
    AdapterTimeout,
    BudgetExceeded,
    ExecutionFailed,
    ProviderUnavailable,
    QualityRejected,
    map_execution_error,
)


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        (TimeoutError("slow"), AdapterTimeout),
        (ConnectionError("offline"), ProviderUnavailable),
        (RuntimeError("broken"), ExecutionFailed),
    ],
)
def test_maps_runtime_errors_to_stable_categories(
    source: Exception,
    expected: type[Exception],
) -> None:
    mapped = map_execution_error(source)

    assert isinstance(mapped, expected)
    assert str(mapped) == str(source)


@pytest.mark.parametrize(
    "error",
    [
        ProviderUnavailable("down"),
        AdapterTimeout("slow"),
        BudgetExceeded("cost"),
        QualityRejected("score"),
        ExecutionFailed("bad"),
    ],
)
def test_preserves_already_classified_errors(error: Exception) -> None:
    assert map_execution_error(error) is error
