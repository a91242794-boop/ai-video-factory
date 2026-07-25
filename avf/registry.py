from dataclasses import dataclass
from pathlib import Path
from typing import Any

from avf.yamlio import load_yaml_mapping


class RegistryError(ValueError):
    """Raised when a registry cannot be loaded or validated."""


@dataclass(frozen=True)
class Registry:
    storyboard_purposes: tuple[str, ...]
    compiler_target: str
    qa_required_purposes: tuple[str, ...]
    minimum_qa_score: int


def _required(data: dict[str, Any], path: tuple[str, ...]) -> Any:
    value: Any = data
    for key in path:
        if not isinstance(value, dict) or key not in value:
            raise RegistryError(
                f"Registry missing required field: {'.'.join(path)}"
            )
        value = value[key]
    return value


def load_registry(path: str | Path) -> Registry:
    raw = load_yaml_mapping(path, label="Registry", error_type=RegistryError)
    purposes = _required(raw, ("storyboard", "purposes"))
    target = _required(raw, ("compiler", "target"))
    required_purposes = _required(raw, ("qa", "required_purposes"))
    minimum_score = _required(raw, ("qa", "minimum_score"))

    if not isinstance(purposes, list) or not all(
        isinstance(item, str) and item.strip() for item in purposes
    ):
        raise RegistryError("Registry field storyboard.purposes must be a string list")
    if len(purposes) != 6:
        raise RegistryError("Registry field storyboard.purposes must contain 6 items")
    if len(set(purposes)) != len(purposes):
        raise RegistryError("Registry field storyboard.purposes must be unique")
    if not isinstance(target, str) or not target.strip():
        raise RegistryError("Registry field compiler.target must be a non-empty string")
    if not isinstance(required_purposes, list) or not all(
        isinstance(item, str) and item.strip() for item in required_purposes
    ):
        raise RegistryError("Registry field qa.required_purposes must be a string list")
    if required_purposes != purposes:
        raise RegistryError(
            "Registry field qa.required_purposes must match storyboard.purposes"
        )
    if type(minimum_score) is not int or not 0 <= minimum_score <= 100:
        raise RegistryError("Registry field qa.minimum_score must be between 0 and 100")

    return Registry(
        storyboard_purposes=tuple(purposes),
        compiler_target=target,
        qa_required_purposes=tuple(required_purposes),
        minimum_qa_score=minimum_score,
    )
