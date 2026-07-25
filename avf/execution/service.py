"""Unified resilient provider selection and adapter execution boundary."""

from dataclasses import replace
from time import perf_counter

from avf.adapters.base import AdapterContract
from avf.adapters.registry import AdapterRegistry
from avf.capabilities.registry import ProviderDescriptor
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
from avf.resilience.errors import (
    AdapterTimeout,
    ExecutionFailed,
    ProviderUnavailable,
    map_execution_error,
)
from avf.resilience.fallback import FallbackPolicy
from avf.resilience.policy import CostGuard
from avf.resilience.retry import RetryPolicy
from avf.router.exceptions import NoProviderAvailableError
from avf.router.router import ProviderRouter

_RETRYABLE_FAILURES = (
    ProviderUnavailable,
    AdapterTimeout,
    ExecutionFailed,
)


class ExecutionService:
    """Validate, route, retry, fall back, execute, and trace a request."""

    def __init__(
        self,
        router: ProviderRouter,
        adapters: AdapterRegistry,
        *,
        retry_policy: RetryPolicy | None = None,
        fallback_policy: FallbackPolicy | None = None,
        cost_guard: CostGuard | None = None,
    ) -> None:
        self._router = router
        self._adapters = adapters
        self._retry_policy = retry_policy or RetryPolicy()
        self._fallback_policy = fallback_policy or FallbackPolicy(router)
        self._cost_guard = cost_guard or CostGuard()

    def execute(
        self,
        request: CapabilityRequest,
        context: ExecutionContext,
    ) -> CapabilityResult:
        self._validate(request, context)
        budget = self._effective_budget(request, context)
        routed_request = replace(request, max_cost=budget)
        candidates = self._candidates(routed_request, request, budget)
        fallback_path: list[str] = []
        retry_count = 0
        last_failure: Exception | None = None
        started = perf_counter()

        for index, provider in enumerate(candidates):
            fallback_path.append(provider.provider_id)
            estimated_cost = self._cost_guard.check(provider, budget)
            try:
                adapter = self._adapters.get(provider.provider_id)
            except KeyError as error:
                if len(candidates) == 1:
                    raise ExecutionAdapterNotFoundError(
                        "No adapter registered for provider "
                        f"{provider.provider_id}"
                    ) from error
                last_failure = ProviderUnavailable(
                    f"No adapter registered for provider {provider.provider_id}"
                )
                self._record_fallback(
                    context,
                    provider,
                    candidates[index + 1],
                    fallback_path,
                    estimated_cost,
                )
                continue

            if adapter.capability is not request.capability:
                raise ExecutionValidationError(
                    f"Adapter {adapter.provider_id} does not support "
                    f"{request.capability.value}"
                )

            def on_retry(attempt: int, error: Exception) -> None:
                nonlocal retry_count
                retry_count += 1
                context.trace.append(
                    {
                        "event": "execution_retry",
                        "request_id": context.request_id,
                        "provider": provider.provider_id,
                        "adapter": adapter.provider_id,
                        "retry_count": attempt,
                        "fallback_path": list(fallback_path),
                        "cost": {"estimated": estimated_cost},
                        "error": type(error).__name__,
                    }
                )

            try:
                outcome = self._retry_policy.run(
                    lambda: self._execute_adapter(adapter, request),
                    on_retry=on_retry,
                )
            except _RETRYABLE_FAILURES as error:
                last_failure = error
                if index + 1 < len(candidates):
                    self._record_fallback(
                        context,
                        provider,
                        candidates[index + 1],
                        fallback_path,
                        estimated_cost,
                    )
                    continue
                raise

            result = outcome.value
            duration = perf_counter() - started
            metrics = ExecutionMetrics(
                estimated_cost=estimated_cost,
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
                    "provider": provider.provider_id,
                    "adapter": adapter.provider_id,
                    "retry_count": retry_count,
                    "fallback_path": list(fallback_path),
                    "cost": {
                        "estimated": estimated_cost,
                        "actual": result.metrics.actual_cost,
                    },
                    "metrics": metrics.to_dict(),
                }
            )
            return result

        if last_failure is not None:
            raise last_failure
        raise ExecutionProviderNotFoundError(
            f"No provider available for capability {request.capability.value}"
        )

    @staticmethod
    def _execute_adapter(
        adapter: AdapterContract,
        request: CapabilityRequest,
    ) -> CapabilityResult:
        try:
            result = adapter.execute(request)
        except Exception as error:
            mapped = map_execution_error(error)
            if mapped is error:
                raise
            raise mapped from error
        if not result.success:
            raise ExecutionFailed(
                "; ".join(result.issues)
                or "Adapter returned an unsuccessful result"
            )
        return result

    def _candidates(
        self,
        routed_request: CapabilityRequest,
        original_request: CapabilityRequest,
        budget: float | None,
    ) -> list[ProviderDescriptor]:
        try:
            return self._fallback_policy.candidates(routed_request)
        except NoProviderAvailableError as error:
            if budget is not None:
                raise ExecutionBudgetExceededError(
                    f"No provider available within budget {budget} "
                    f"for capability {original_request.capability.value}"
                ) from error
            raise ExecutionProviderNotFoundError(
                "No provider available for capability "
                f"{original_request.capability.value}"
            ) from error

    @staticmethod
    def _record_fallback(
        context: ExecutionContext,
        current: ProviderDescriptor,
        following: ProviderDescriptor,
        fallback_path: list[str],
        estimated_cost: float,
    ) -> None:
        context.trace.append(
            {
                "event": "execution_fallback",
                "request_id": context.request_id,
                "provider": current.provider_id,
                "adapter": current.provider_id,
                "retry_count": 0,
                "fallback_path": list(fallback_path)
                + [following.provider_id],
                "cost": {"estimated": estimated_cost},
                "next_provider": following.provider_id,
            }
        )

    @staticmethod
    def _validate(
        request: CapabilityRequest,
        context: ExecutionContext,
    ) -> None:
        if not isinstance(request, CapabilityRequest):
            raise ExecutionValidationError(
                "request must be a CapabilityRequest"
            )
        if not isinstance(context, ExecutionContext):
            raise ExecutionValidationError(
                "context must be an ExecutionContext"
            )

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
