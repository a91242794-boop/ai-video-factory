"""Stable execution failure categories used by resilience policies."""


class ResilienceError(RuntimeError):
    """Base class for classified execution failures."""


class ProviderUnavailable(ResilienceError):
    """A provider cannot accept or complete work."""


class AdapterTimeout(ResilienceError):
    """An adapter exceeded its allowed execution time."""


class BudgetExceeded(ResilienceError):
    """A paid provider cannot run within the execution budget."""


class QualityRejected(ResilienceError):
    """A result did not meet the required quality threshold."""


class ExecutionFailed(ResilienceError):
    """An execution failed without a more specific classification."""


def map_execution_error(error: Exception) -> ResilienceError:
    """Map runtime exceptions to stable resilience categories."""
    if isinstance(error, ResilienceError):
        return error
    if isinstance(error, TimeoutError):
        return AdapterTimeout(str(error))
    if isinstance(error, ConnectionError):
        return ProviderUnavailable(str(error))
    return ExecutionFailed(str(error))
