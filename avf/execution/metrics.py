"""Provider-neutral metrics produced by the execution boundary."""

from dataclasses import asdict, dataclass

from avf.execution.errors import ExecutionValidationError


@dataclass(frozen=True)
class ExecutionMetrics:
    estimated_cost: float
    actual_cost: float
    tokens: int
    duration: float
    provider_id: str
    adapter_id: str

    def __post_init__(self) -> None:
        for name in ("estimated_cost", "actual_cost", "duration"):
            if getattr(self, name) < 0:
                raise ExecutionValidationError(
                    f"{name} must be zero or greater"
                )
        if self.tokens < 0:
            raise ExecutionValidationError(
                "tokens must be zero or greater"
            )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
