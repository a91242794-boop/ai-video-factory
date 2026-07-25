"""Execution-layer errors with stable, caller-facing meanings."""


class ExecutionError(RuntimeError):
    """Base error for failures before or during capability execution."""


class ExecutionValidationError(ExecutionError):
    """The request or execution context is invalid."""


class ExecutionProviderNotFoundError(ExecutionError):
    """No provider can satisfy the capability request."""


class ExecutionAdapterNotFoundError(ExecutionError):
    """The selected provider has no registered executable adapter."""


class ExecutionBudgetExceededError(ExecutionError):
    """No provider can execute within the effective budget."""
