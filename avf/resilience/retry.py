"""Bounded synchronous retry mechanism for classified failures."""

from dataclasses import dataclass
from typing import Callable, Generic, TypeVar

from avf.resilience.errors import (
    AdapterTimeout,
    ExecutionFailed,
    ProviderUnavailable,
)

T = TypeVar("T")
_RETRYABLE = (ProviderUnavailable, AdapterTimeout, ExecutionFailed)


@dataclass(frozen=True)
class RetryOutcome(Generic[T]):
    value: T
    retry_count: int


@dataclass(frozen=True)
class RetryPolicy:
    max_retries: int = 0

    def __post_init__(self) -> None:
        if self.max_retries < 0:
            raise ValueError("max_retries must be zero or greater")

    def run(
        self,
        operation: Callable[[], T],
        on_retry: Callable[[int, Exception], None] | None = None,
    ) -> RetryOutcome[T]:
        retry_count = 0
        while True:
            try:
                return RetryOutcome(operation(), retry_count)
            except _RETRYABLE as error:
                if retry_count >= self.max_retries:
                    raise
                retry_count += 1
                if on_retry is not None:
                    on_retry(retry_count, error)
