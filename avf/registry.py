from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


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
            dotted = ".".join(path)
            raise RegistryError(f"Registry missing required field: {dotted}")
        value = value[key]
    return value


def load_registry(path: str | Path) -> Registry:
    registry_path = Path(path)
    if not registry_path.is_file():
        raise RegistryError(f"Registry file not found: {registry_path}")

    try:
        raw = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise RegistryError(f"Invalid registry YAML: {registry_path}") from exc

    if not isinstance(raw, dict):
        raise RegistryError("Registry root must be a mapping")

    purposes = _required(raw, ("storyboard", "purposes"))
    target = _required(raw, ("compiler", "target"))
    required_purposes = _required(raw, ("qa", "required_purposes"))
    minimum_score = _required(raw, ("qa", "minimum_score"))

    if not isinstance(purposes, list) or not all(
        isinstance(item, str) and item for item in purposes
    ):
        raise RegistryError("Registry field storyboard.purposes must be a string list")
    if not isinstance(target, str) or not target:
        raise RegistryError("Registry field compiler.target must be a non-empty string")
    if not isinstance(required_purposes, list) or not all(
        isinstance(item, str) and item for item in required_purposes
    ):
        raise RegistryError("Registry field qa.required_purposes must be a string list")
    if not isinstance(minimum_score, int) or not 0 <= minimum_score <= 100:
        raise RegistryError("Registry field qa.minimum_score must be between 0 and 100")

    return Registry(
        storyboard_purposes=tuple(purposes),
        compiler_target=target,
        qa_required_purposes=tuple(required_purposes),
        minimum_qa_score=minimum_score,
    )

