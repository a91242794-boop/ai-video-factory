"""Provider-neutral request models for AVF capabilities."""

from dataclasses import dataclass, field, fields, is_dataclass
from enum import Enum
from pathlib import Path
from typing import Mapping, Sequence

from avf.capabilities.errors import CapabilityError
from avf.capabilities.types import (
    CapabilityType,
    CostTier,
    QualityTier,
    SpeedTier,
)


def _stable_value(value: object) -> object:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Path):
        return str(value)
    if is_dataclass(value) and not isinstance(value, type):
        return {
            item.name: _stable_value(getattr(value, item.name))
            for item in fields(value)
        }
    if isinstance(value, Mapping):
        return {
            str(key): _stable_value(value[key])
            for key in sorted(value, key=lambda item: str(item))
        }
    if isinstance(value, (tuple, list)):
        return [_stable_value(item) for item in value]
    return value


@dataclass(frozen=True, kw_only=True)
class CapabilityRequest:
    capability: CapabilityType
    project_id: str
    cost_tier: CostTier = CostTier.BALANCED
    quality_tier: QualityTier = QualityTier.STANDARD
    speed_tier: SpeedTier = SpeedTier.BALANCED
    max_cost: float | None = None
    preferred_providers: Sequence[str] = ()
    excluded_providers: Sequence[str] = ()
    metadata: dict[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.max_cost is not None and self.max_cost < 0:
            raise CapabilityError("max_cost must be zero or greater")

        preferred = tuple(self.preferred_providers)
        excluded = tuple(self.excluded_providers)
        overlap = sorted(set(preferred) & set(excluded))
        if overlap:
            raise CapabilityError(
                "preferred_providers and excluded_providers overlap: "
                + ", ".join(overlap)
            )

        object.__setattr__(self, "preferred_providers", preferred)
        object.__setattr__(self, "excluded_providers", excluded)
        object.__setattr__(self, "metadata", dict(self.metadata))

    def to_dict(self) -> dict[str, object]:
        """Serialize the request to a stable, provider-neutral mapping."""
        return {
            item.name: _stable_value(getattr(self, item.name))
            for item in fields(self)
        }


@dataclass(frozen=True, kw_only=True)
class DirectorRequest(CapabilityRequest):
    capability: CapabilityType = field(
        default=CapabilityType.DIRECTOR,
        init=False,
    )
    project_path: str | Path | None = None
    project_data: Mapping[str, object] | None = None
    shot_count: int = 6

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.project_path is None and self.project_data is None:
            raise CapabilityError(
                "DirectorRequest requires project_path or project_data"
            )
        if self.shot_count <= 0:
            raise CapabilityError("shot_count must be greater than zero")


@dataclass(frozen=True, kw_only=True)
class ImageGenerationRequest(CapabilityRequest):
    capability: CapabilityType = field(
        default=CapabilityType.IMAGE_GENERATION,
        init=False,
    )
    storyboard: object
    reference_images: Sequence[str] = ()
    output_format: str = "png"

    def __post_init__(self) -> None:
        super().__post_init__()
        object.__setattr__(self, "reference_images", tuple(self.reference_images))


@dataclass(frozen=True, kw_only=True)
class VideoGenerationRequest(CapabilityRequest):
    capability: CapabilityType = field(
        default=CapabilityType.VIDEO_GENERATION,
        init=False,
    )
    storyboard: object
    image_assets: Sequence[object] = ()
    duration_seconds: float

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.duration_seconds < 0:
            raise CapabilityError("duration_seconds must be zero or greater")
        object.__setattr__(self, "image_assets", tuple(self.image_assets))


@dataclass(frozen=True, kw_only=True)
class QARequest(CapabilityRequest):
    capability: CapabilityType = field(
        default=CapabilityType.QUALITY_ASSURANCE,
        init=False,
    )
    target_type: str
    payload: object
    minimum_score: int

    def __post_init__(self) -> None:
        super().__post_init__()
        if not 0 <= self.minimum_score <= 100:
            raise CapabilityError("minimum_score must be between 0 and 100")
