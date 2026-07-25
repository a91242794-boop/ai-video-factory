"""Unified provider selection and adapter execution boundary."""

from dataclasses import replace
from time import perf_counter

from avf.adapters.registry import AdapterRegistry
from avf.capabilities.requests import CapabilityRequest
from avf.capabilities.results import CapabilityResult
from avf.execution.context import ExecutionContext
from avf.execution.errors import (
    ExecutionAdapterNotFoundError,
    ExecutionBudgetExceededError,
    ExecutionProviderNotFoundError,
    ExecutionValidationError,
)
from avf.execution.metrics import ExecutionMetrics
from avf.router.exceptions import NoProviderAvailableError
from avf.router.policy import RouterPolicy
from avf.router.router import ProviderRouter


class ExecutionService:
    """Validate, route, execute, and trace one capability request."""

    def __init__(
        self,
        router: ProviderRouter,
        adapters: AdapterRegistry,
    ) -> None:
        self._router = router
        self._adapters = adapters

    def execute(
        self,
        request: CapabilityRequest,
        context: ExecutionContext,
    ) -> CapabilityResult:
        if not isinstance(request, CapabilityRequest):
            raise ExecutionValidationError(
                "request must be a CapabilityRequest"
            )
        if not isinstance(context, ExecutionContext):
            raise ExecutionValidationError(
                "context must be an ExecutionContext"
            )

        routed_request = replace(
            request,
            max_cost=self._effective_budget(request, context),
        )
        try:
            provider = self._router.select(routed_request)
        except NoProviderAvailableError as exc:
            if routed_request.max_cost is not None:
                raise ExecutionBudgetExceededError(
                    "No provider available within budget "
                    f"{routed_request.max_cost} for capability "
                    f"{request.capability.value}"
                ) from exc
            raise ExecutionProviderNotFoundError(
                "No provider available for capability "
                f"{request.capability.value}"
            ) from exc

        try:
            adapter = self._adapters.get(provider.provider_id)
        except KeyError as exc:
            raise ExecutionAdapterNotFoundError(
                f"No adapter registered for provider {provider.provider_id}"
            ) from exc
        if adapter.capability is not request.capability:
            raise ExecutionValidationError(
                f"Adapter {adapter.provider_id} does not support "
                f"{request.capability.value}"
            )

        started = perf_counter()
        result = adapter.execute(request)
        duration = perf_counter() - started
        estimated_cost = RouterPolicy.estimated_cost(provider)
        metrics = ExecutionMetrics(
            estimated_cost=(
                result.metrics.estimated_cost
                if estimated_cost is None
                else estimated_cost
            ),
            actual_cost=result.metrics.actual_cost,
            tokens=result.metrics.model_tokens_used,
            duration=duration,
            provider_id=provider.provider_id,
            adapter_id=adapter.provider_id,
        )
        context.trace.append(
            {
                "event": "execution_completed",
                "request_id": context.request_id,
                "metrics": metrics.to_dict(),
            }
        )
        return result

    @staticmethod
    def _effective_budget(
        request: CapabilityRequest,
        context: ExecutionContext,
    ) -> float | None:
        limits = (
            limit
            for limit in (request.max_cost, context.budget_limit)
            if limit is not None
        )
        return min(limits, default=None)
