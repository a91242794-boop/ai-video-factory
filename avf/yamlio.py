from pathlib import Path
from typing import Any, TypeVar

import yaml
from yaml.constructor import ConstructorError
from yaml.nodes import MappingNode


ErrorT = TypeVar("ErrorT", bound=ValueError)


class UniqueKeyLoader(yaml.SafeLoader):
    """Safe YAML loader that rejects duplicate mapping keys."""


def _construct_unique_mapping(
    loader: UniqueKeyLoader,
    node: MappingNode,
    deep: bool = False,
) -> dict[Any, Any]:
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"found duplicate key: {key}",
                key_node.start_mark,
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_unique_mapping,
)


def load_yaml_mapping(
    path: str | Path,
    *,
    label: str,
    error_type: type[ErrorT],
) -> dict[str, Any]:
    config_path = Path(path)
    if not config_path.is_file():
        raise error_type(f"{label} file not found: {config_path}")
    try:
        raw = yaml.load(
            config_path.read_text(encoding="utf-8"),
            Loader=UniqueKeyLoader,
        )
    except (UnicodeError, yaml.YAMLError) as exc:
        detail = getattr(exc, "problem", None)
        suffix = f": {detail}" if detail else ""
        raise error_type(f"Invalid {label.lower()} YAML: {config_path}{suffix}") from exc
    if not isinstance(raw, dict):
        raise error_type(f"{label} root must be a mapping")
    return raw
