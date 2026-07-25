"""Public API for AVF fault-tolerance policies."""

from avf.resilience.errors import (
    AdapterTimeout,
    BudgetExceeded,
    ExecutionFailed,
    ProviderUnavailable,
    QualityRejected,
    ResilienceError,
    map_execution_error,
)
from avf.resilience.fallback import FallbackPolicy
from avf.resilience.policy import CostGuard
from avf.resilience.retry import RetryOutcome, RetryPolicy

__all__ = [
    "AdapterTimeout",
    "BudgetExceeded",
    "CostGuard",
    "ExecutionFailed",
    "FallbackPolicy",
    "ProviderUnavailable",
    "QualityRejected",
    "ResilienceError",
    "RetryOutcome",
    "RetryPolicy",
    "map_execution_error",
]
