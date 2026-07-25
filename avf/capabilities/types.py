"""Stable enums shared by capability requests, results, and registries."""

from enum import Enum
from typing import Self

from avf.capabilities.errors import CapabilityError


class _StableStringEnum(str, Enum):
    @classmethod
    def parse(cls, value: str) -> Self:
        """Parse a stable string value with a domain-specific error."""
        try:
            return cls(value)
        except (TypeError, ValueError) as exc:
            raise CapabilityError(
                f"Unsupported {cls.__name__} value: {value!r}"
            ) from exc


class CapabilityType(_StableStringEnum):
    DIRECTOR = "director"
    IMAGE_GENERATION = "image_generation"
    VIDEO_GENERATION = "video_generation"
    QUALITY_ASSURANCE = "quality_assurance"


class CostTier(_StableStringEnum):
    FREE = "free"
    LOW = "low"
    BALANCED = "balanced"
    PREMIUM = "premium"


class QualityTier(_StableStringEnum):
    DRAFT = "draft"
    STANDARD = "standard"
    HIGH = "high"
    PREMIUM = "premium"


class SpeedTier(_StableStringEnum):
    SLOW = "slow"
    BALANCED = "balanced"
    FAST = "fast"
