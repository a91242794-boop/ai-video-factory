from pathlib import Path

import pytest

from avf.project import ProjectError, load_project


ROOT = Path(__file__).parents[1]


def test_load_mini_project_returns_typed_configuration():
    project = load_project(ROOT / "examples" / "mini" / "project.yaml")

    assert project.project.id == "avf-mini-demo"
    assert project.product.name == "Daily Scalp Care Serum"
    assert project.product.key_features == ("lightweight texture", "simple daily use")
    assert project.market.language == "en-US"
    assert project.video.shot_count == 6
    assert project.creative.cta == "Discover your daily care routine"


def test_load_project_rejects_non_six_shot_configuration(tmp_path):
    project_file = tmp_path / "project.yaml"
    project_file.write_text(_valid_project_yaml().replace("shot_count: 6", "shot_count: 8"))

    with pytest.raises(ProjectError, match="shot_count must equal 6"):
        load_project(project_file)


def test_load_project_reports_missing_required_field(tmp_path):
    project_file = tmp_path / "project.yaml"
    project_file.write_text(_valid_project_yaml().replace("  cta: Buy now\n", ""))

    with pytest.raises(ProjectError, match="creative.cta"):
        load_project(project_file)


def test_load_project_reports_invalid_yaml(tmp_path):
    project_file = tmp_path / "project.yaml"
    project_file.write_text("project: [", encoding="utf-8")

    with pytest.raises(ProjectError, match="Invalid project YAML"):
        load_project(project_file)


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
