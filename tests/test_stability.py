import subprocess
import sys
from pathlib import Path

import pytest

from avf.project import ProjectError, load_project
from avf.registry import RegistryError, load_registry


ROOT = Path(__file__).parents[1]


def test_project_rejects_duplicate_yaml_keys(tmp_path):
    project_file = tmp_path / "project.yaml"
    project_file.write_text(
        _valid_project_yaml().replace(
            "  name: Test Project\n",
            "  name: First Name\n  name: Second Name\n",
        ),
        encoding="utf-8",
    )

    with pytest.raises(ProjectError, match="duplicate key.*name"):
        load_project(project_file)


@pytest.mark.parametrize(
    ("old", "new", "message"),
    [
        ("shot_count: 6", "shot_count: true", "video.shot_count"),
        ("duration_seconds: 15", "duration_seconds: true", "video.duration_seconds"),
        ("key_features: [easy use]", "key_features: []", "product.key_features"),
        ("reference_images: [product.png]", "reference_images: []", "product.reference_images"),
    ],
)
def test_project_rejects_ambiguous_or_empty_values(tmp_path, old, new, message):
    project_file = tmp_path / "project.yaml"
    project_file.write_text(
        _valid_project_yaml().replace(old, new),
        encoding="utf-8",
    )

    with pytest.raises(ProjectError, match=message):
        load_project(project_file)


def test_registry_rejects_duplicate_yaml_keys(tmp_path):
    registry_file = tmp_path / "registry.yaml"
    registry_file.write_text(
        _valid_registry_yaml().replace(
            "  minimum_score: 90",
            "  minimum_score: 80\n  minimum_score: 90",
        ),
        encoding="utf-8",
    )

    with pytest.raises(RegistryError, match="duplicate key.*minimum_score"):
        load_registry(registry_file)


@pytest.mark.parametrize(
    ("replacement", "message"),
    [
        ("minimum_score: true", "qa.minimum_score"),
        (
            "required_purposes: [hook, problem, product_reveal, use, benefit, wrong]",
            "must match",
        ),
        (
            "purposes: [hook, hook, product_reveal, use, benefit, cta_plate]",
            "unique",
        ),
    ],
)
def test_registry_rejects_inconsistent_values(tmp_path, replacement, message):
    registry_file = tmp_path / "registry.yaml"
    source = _valid_registry_yaml()
    if replacement.startswith("minimum_score"):
        source = source.replace("minimum_score: 90", replacement)
    elif replacement.startswith("required_purposes"):
        source = source.replace(
            "required_purposes: [hook, problem, product_reveal, use, benefit, cta_plate]",
            replacement,
        )
    else:
        source = source.replace(
            "purposes: [hook, problem, product_reveal, use, benefit, cta_plate]",
            replacement,
        )
    registry_file.write_text(source, encoding="utf-8")

    with pytest.raises(RegistryError, match=message):
        load_registry(registry_file)


def test_cli_invalid_project_returns_2_without_traceback(tmp_path):
    project_file = tmp_path / "project.yaml"
    project_file.write_text("project: [", encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "avf.cli",
            "run",
            "--project",
            str(project_file),
            "--registry",
            str(ROOT / "registry" / "default.yaml"),
            "--output",
            str(tmp_path / "output"),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 2
    assert "AVF error:" in result.stderr
    assert "Traceback" not in result.stderr


def _valid_project_yaml() -> str:
    return """\
project:
  id: test
  name: Test Project
product:
  name: Test Product
  category: care
  key_features: [easy use]
  reference_images: [product.png]
market:
  country: Mexico
  language: es-MX
  platform: TikTok
  audience: adults
video:
  duration_seconds: 15
  shot_count: 6
  aspect_ratio: "9:16"
creative:
  hook: A visible daily problem
  tone: realistic
  environment: bright bathroom
  character: adult creator
  cta: Buy now
"""


def _valid_registry_yaml() -> str:
    return """\
storyboard:
  purposes: [hook, problem, product_reveal, use, benefit, cta_plate]
compiler:
  target: gpt-image
qa:
  required_purposes: [hook, problem, product_reveal, use, benefit, cta_plate]
  minimum_score: 90
"""
