import pytest

from avf.resilience import (
    AdapterTimeout,
    ExecutionFailed,
    ProviderUnavailable,
    RetryPolicy,
)


@pytest.mark.parametrize(
    "error",
    [ProviderUnavailable("down"), AdapterTimeout("slow"), ExecutionFailed("bad")],
)
def test_retry_policy_retries_supported_failures(error: Exception) -> None:
    attempts = 0

    def operation() -> str:
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise error
        return "ok"

    outcome = RetryPolicy(max_retries=2).run(operation)

    assert outcome.value == "ok"
    assert outcome.retry_count == 2
    assert attempts == 3


def test_retry_policy_stops_after_configured_maximum() -> None:
    attempts = 0

    def operation() -> None:
        nonlocal attempts
        attempts += 1
        raise ProviderUnavailable("down")

    with pytest.raises(ProviderUnavailable, match="down"):
        RetryPolicy(max_retries=1).run(operation)

    assert attempts == 2


def test_retry_policy_does_not_retry_non_retryable_failure() -> None:
    attempts = 0

    def operation() -> None:
        nonlocal attempts
        attempts += 1
        raise ValueError("invalid")

    with pytest.raises(ValueError, match="invalid"):
        RetryPolicy(max_retries=5).run(operation)

    assert attempts == 1
