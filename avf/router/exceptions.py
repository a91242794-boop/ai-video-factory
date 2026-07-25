"""Errors raised while selecting a declared provider."""


class ProviderRouterError(RuntimeError):
    """Base error for provider routing failures."""


class NoProviderAvailableError(ProviderRouterError):
    """Raised when no registered provider satisfies a request."""


class InvalidProviderCostError(ProviderRouterError):
    """Raised when declared provider cost metadata is invalid."""
