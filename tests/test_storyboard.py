from dataclasses import asdict
from pathlib import Path

import yaml

from avf.project import load_project
from avf.storyboard import generate_storyboard


ROOT = Path(__file__).parents[1]
PURPOSES = (
    "hook",
    "problem",
    "product_reveal",
    "use",
    "benefit",
    "cta_plate",
)


def test_generate_storyboard_has_exact_required_sequence_and_fields():
    project = load_project(ROOT / "examples" / "mini" / "project.yaml")

    storyboard = generate_storyboard(project)

    assert len(storyboard.shots) == 6
    assert tuple(shot.id for shot in storyboard.shots) == (1, 2, 3, 4, 5, 6)
    assert tuple(shot.purpose for shot in storyboard.shots) == PURPOSES
    for shot in storyboard.shots:
        assert shot.duration > 0
        assert shot.shot
        assert shot.visual
        assert shot.action
        assert shot.product_visibility
        assert shot.continuity


def test_generate_storyboard_respects_duration_and_product_reveal():
    project = load_project(ROOT / "examples" / "mini" / "project.yaml")

    storyboard = generate_storyboard(project)

    assert sum(shot.duration for shot in storyboard.shots) <= project.video.duration_seconds
    reveal = next(shot for shot in storyboard.shots if shot.purpose == "product_reveal")
    assert reveal.id <= 3
    assert reveal.product_visibility == "hero"


def test_generate_storyboard_is_deterministic_and_yaml_serializable():
    project = load_project(ROOT / "examples" / "mini" / "project.yaml")

    first = generate_storyboard(project)
    second = generate_storyboard(project)
    encoded = yaml.safe_dump(asdict(first), sort_keys=False)

    assert first == second
    assert yaml.safe_load(encoded)["shots"][5]["purpose"] == "cta_plate"
