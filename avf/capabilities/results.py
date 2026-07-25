"""Provider-neutral results and execution metrics for AVF capabilities."""

from dataclasses import dataclass, field, fields
from typing import Sequence

from avf.capabilities.errors import CapabilityError
from avf.capabilities.requests import _stable_value
from avf.capabilities.types import CapabilityType


@dataclass(frozen=True, kw_only=True)
class RunMetrics:
    estimated_cost: float = 0
    actual_cost: float = 0
    duration_seconds: float = 0
    quality_score: float | None = None
    fallback_count: int = 0
    model_tokens_used: int = 0
    cache_hit: bool = False

    def __post_init__(self) -> None:
        for name in ("estimated_cost", "actual_cost", "duration_seconds"):
            if getattr(self, name) < 0:
                raise CapabilityError(f"{name} must be zero or greater")
        if self.quality_score is not None and not 0 <= self.quality_score <= 100:
            raise CapabilityError("quality_score must be between 0 and 100")
        for name in ("fallback_count", "model_tokens_used"):
            if getattr(self, name) < 0:
                raise CapabilityError(f"{name} must be zero or greater")

    def to_dict(self) -> dict[str, object]:
        return {
            item.name: _stable_value(getattr(self, item.name))
            for item in fields(self)
        }


@dataclass(frozen=True, kw_only=True)
class CapabilityResult:
    capability: CapabilityType
    provider: str
    success: bool
    output: object = None
    issues: Sequence[str] = field(default_factory=list)
    metrics: RunMetrics = field(default_factory=RunMetrics)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "issues",
            list(self.issues),
        )

    def to_dict(self) -> dict[str, object]:
        """Serialize the result and metrics to a stable mapping."""
        return {
            item.name: _stable_value(getattr(self, item.name))
            for item in fields(self)
        }
