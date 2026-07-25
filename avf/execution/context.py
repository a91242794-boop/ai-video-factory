"""Per-request execution context and trace state."""

from dataclasses import dataclass, field

from avf.execution.errors import ExecutionValidationError


@dataclass
class ExecutionContext:
    request_id: str
    budget_limit: float | None = None
    cost_policy: str = "free_first"
    trace: list[dict[str, object]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.request_id.strip():
            raise ExecutionValidationError(
                "request_id must be a non-empty string"
            )
        if self.budget_limit is not None and self.budget_limit < 0:
            raise ExecutionValidationError(
                "budget_limit must be zero or greater"
            )
        if not self.cost_policy.strip():
            raise ExecutionValidationError(
                "cost_policy must be a non-empty string"
            )
        self.trace = list(self.trace)
