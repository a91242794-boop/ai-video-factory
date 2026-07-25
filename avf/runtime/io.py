"""Typed, provider-neutral module input/output value objects."""

from dataclasses import dataclass, field
from math import isfinite
from typing import Any

from avf.runtime.context import ExecutionContext


def _validate_metadata(metadata: object) -> dict[str, Any]:
    if not isinstance(metadata, dict):
        raise TypeError("metadata must be a dictionary")
    if any(not isinstance(key, str) for key in metadata):
        raise TypeError("metadata keys must be strings")
    return dict(metadata)


def _validate_cost(cost: object) -> None:
    if (
        isinstance(cost, bool)
        or not isinstance(cost, (int, float))
        or not isfinite(cost)
        or cost < 0
    ):
        raise ValueError("cost must be a finite number zero or greater")


@dataclass(frozen=True, kw_only=True)
class Artifact:
    artifact_id: str
    artifact_type: str
    data: Any
    metadata: dict[str, Any] = field(default_factory=dict)
    cost: float = 0

    def __post_init__(self) -> None:
        for field_name in ("artifact_id", "artifact_type"):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(
                    f"{field_name} must be a non-empty string"
                )
        object.__setattr__(
            self,
            "metadata",
            _validate_metadata(self.metadata),
        )
        _validate_cost(self.cost)


@dataclass(frozen=True, kw_only=True)
class ModuleInput:
    artifacts: tuple[Artifact, ...] = ()
    context: ExecutionContext | None = None

    def __post_init__(self) -> None:
        artifacts = self.artifacts
        if isinstance(artifacts, (str, bytes)) or artifacts is None:
            raise TypeError("artifacts must be an iterable of Artifact")
        try:
            normalized = tuple(artifacts)
        except TypeError as exc:
            raise TypeError(
                "artifacts must be an iterable of Artifact"
            ) from exc
        if any(not isinstance(item, Artifact) for item in normalized):
            raise TypeError("artifacts must contain only Artifact objects")
        object.__setattr__(self, "artifacts", normalized)
        if (
            self.context is not None
            and not isinstance(self.context, ExecutionContext)
        ):
            raise TypeError("context must be an ExecutionContext")


@dataclass(frozen=True, kw_only=True)
class ModuleOutput:
    artifacts: tuple[Artifact, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)
    cost: float = 0

    def __post_init__(self) -> None:
        artifacts = self.artifacts
        if isinstance(artifacts, (str, bytes)) or artifacts is None:
            raise TypeError("artifacts must be an iterable of Artifact")
        try:
            normalized = tuple(artifacts)
        except TypeError as exc:
            raise TypeError(
                "artifacts must be an iterable of Artifact"
            ) from exc
        if any(not isinstance(item, Artifact) for item in normalized):
            raise TypeError("artifacts must contain only Artifact objects")
        object.__setattr__(self, "artifacts", normalized)
        object.__setattr__(
            self,
            "metadata",
            _validate_metadata(self.metadata),
        )
        _validate_cost(self.cost)
