"""Dependency declarations for runtime module ordering."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ModuleDependency:
    module_id: str
    requires: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.module_id.strip():
            raise ValueError("module_id must be a non-empty string")
        if any(not dependency.strip() for dependency in self.requires):
            raise ValueError(
                "dependency identifiers must be non-empty strings"
            )
        if self.module_id in self.requires:
            raise ValueError("module cannot depend on itself")
        if len(set(self.requires)) != len(self.requires):
            raise ValueError("module dependencies must be unique")
