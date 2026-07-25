from pathlib import Path
from typing import Any

import yaml

from avf.models import Creative, Market, Product, Project, ProjectInfo, Video


class ProjectError(ValueError):
    """Raised when a project file cannot be loaded or validated."""


def _required(data: dict[str, Any], path: tuple[str, ...], expected: type) -> Any:
    value: Any = data
    for key in path:
        if not isinstance(value, dict) or key not in value:
            raise ProjectError(f"Project missing required field: {'.'.join(path)}")
        value = value[key]
    if not isinstance(value, expected) or expected is str and not value.strip():
        raise ProjectError(f"Invalid project field: {'.'.join(path)}")
    return value


def _string_list(data: dict[str, Any], path: tuple[str, ...]) -> tuple[str, ...]:
    value = _required(data, path, list)
    if not all(isinstance(item, str) and item.strip() for item in value):
        raise ProjectError(f"Invalid project field: {'.'.join(path)}")
    return tuple(value)


def load_project(path: str | Path) -> Project:
    project_path = Path(path)
    if not project_path.is_file():
        raise ProjectError(f"Project file not found: {project_path}")
    try:
        raw = yaml.safe_load(project_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ProjectError(f"Invalid project YAML: {project_path}") from exc
    if not isinstance(raw, dict):
        raise ProjectError("Project root must be a mapping")

    shot_count = _required(raw, ("video", "shot_count"), int)
    if shot_count != 6:
        raise ProjectError(f"Project video.shot_count must equal 6; got {shot_count}")

    duration = _required(raw, ("video", "duration_seconds"), (int, float))
    if duration <= 0:
        raise ProjectError("Project video.duration_seconds must be greater than 0")

    return Project(
        project=ProjectInfo(
            id=_required(raw, ("project", "id"), str),
            name=_required(raw, ("project", "name"), str),
        ),
        product=Product(
            name=_required(raw, ("product", "name"), str),
            category=_required(raw, ("product", "category"), str),
            key_features=_string_list(raw, ("product", "key_features")),
            reference_images=_string_list(raw, ("product", "reference_images")),
        ),
        market=Market(
            country=_required(raw, ("market", "country"), str),
            language=_required(raw, ("market", "language"), str),
            platform=_required(raw, ("market", "platform"), str),
            audience=_required(raw, ("market", "audience"), str),
        ),
        video=Video(
            duration_seconds=float(duration),
            shot_count=shot_count,
            aspect_ratio=_required(raw, ("video", "aspect_ratio"), str),
        ),
        creative=Creative(
            hook=_required(raw, ("creative", "hook"), str),
            tone=_required(raw, ("creative", "tone"), str),
            environment=_required(raw, ("creative", "environment"), str),
            character=_required(raw, ("creative", "character"), str),
            cta=_required(raw, ("creative", "cta"), str),
        ),
    )

