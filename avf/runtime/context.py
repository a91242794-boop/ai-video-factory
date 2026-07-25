"""Immutable inputs shared across one runtime execution."""

from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class ExecutionContext:
    project_id: str
    budget: float
    quality_target: float
    market: str
    locale: str

    def __post_init__(self) -> None:
        for field_name in ("project_id", "market", "locale"):
            value = getattr(self, field_name)
            if not value.strip():
                raise ValueError(
                    f"{field_name} must be a non-empty string"
                )
        if self.budget < 0:
            raise ValueError("budget must be zero or greater")
        if not 0 <= self.quality_target <= 100:
            raise ValueError(
                "quality_target must be between 0 and 100"
            )
