"""Stable metadata and lifecycle types for AVF runtime modules."""

from dataclasses import dataclass
from enum import Enum


class ModuleState(str, Enum):
    CREATED = "created"
    INITIALIZED = "initialized"
    RUNNING = "running"
    STOPPED = "stopped"


@dataclass(frozen=True, kw_only=True)
class ModuleMetadata:
    module_id: str
    name: str
    version: str
    cost: float = 0

    def __post_init__(self) -> None:
        for field_name in ("module_id", "name", "version"):
            value = getattr(self, field_name)
            if not value.strip():
                raise ValueError(
                    f"{field_name} must be a non-empty string"
                )
        if self.cost != 0:
            raise ValueError("module cost must remain zero")
