from pathlib import Path

import pytest

from avf.registry import RegistryError, load_registry


ROOT = Path(__file__).parents[1]


def test_load_default_registry_returns_structured_values():
    registry = load_registry(ROOT / "registry" / "default.yaml")

    assert registry.storyboard_purposes == (
        "hook",
        "problem",
        "product_reveal",
        "use",
        "benefit",
        "cta_plate",
    )
    assert registry.compiler_target == "gpt-image"
    assert registry.qa_required_purposes == registry.storyboard_purposes
    assert registry.minimum_qa_score == 90


def test_load_registry_reports_missing_file(tmp_path):
    missing = tmp_path / "missing.yaml"

    with pytest.raises(RegistryError, match="Registry file not found"):
        load_registry(missing)


def test_load_registry_reports_invalid_yaml(tmp_path):
    invalid = tmp_path / "invalid.yaml"
    invalid.write_text("storyboard: [", encoding="utf-8")

    with pytest.raises(RegistryError, match="Invalid registry YAML"):
        load_registry(invalid)


def test_load_registry_reports_missing_required_field(tmp_path):
    incomplete = tmp_path / "incomplete.yaml"
    incomplete.write_text("storyboard:\n  purposes: [hook]\n", encoding="utf-8")

    with pytest.raises(RegistryError, match="missing required field"):
        load_registry(incomplete)
