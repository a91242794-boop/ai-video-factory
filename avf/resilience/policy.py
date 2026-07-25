"""Cost enforcement immediately before adapter execution."""

from avf.capabilities.registry import ProviderDescriptor
from avf.resilience.errors import BudgetExceeded
from avf.router.policy import RouterPolicy


class CostGuard:
    def check(
        self,
        provider: ProviderDescriptor,
        budget_limit: float | None,
    ) -> float:
        estimated_cost = RouterPolicy.estimated_cost(provider)
        if estimated_cost is None:
            if budget_limit is None:
                return 0
            raise BudgetExceeded(
                f"Provider {provider.provider_id} has unknown estimated cost"
            )
        if budget_limit is not None and estimated_cost > budget_limit:
            raise BudgetExceeded(
                f"Provider {provider.provider_id} estimated cost "
                f"{estimated_cost} exceeds budget {budget_limit}"
            )
        return estimated_cost
