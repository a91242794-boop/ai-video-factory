"""Validated quality scores shared across intelligence components."""

from dataclasses import dataclass


@dataclass(frozen=True, order=True)
class QualityScore:
    value: float

    def __post_init__(self) -> None:
        if isinstance(self.value, bool) or not isinstance(
            self.value,
            (int, float),
        ):
            raise ValueError("quality score must be a number")
        if not 0 <= self.value <= 100:
            raise ValueError("quality score must be between 0 and 100")
