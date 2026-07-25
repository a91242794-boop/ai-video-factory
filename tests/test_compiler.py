from pathlib import Path

from avf.compiler import compile_gpt_image_prompt
from avf.project import load_project
from avf.registry import load_registry
from avf.storyboard import generate_storyboard


ROOT = Path(__file__).parents[1]


def test_compile_prompt_contains_layout_locks_shots_and_constraints():
    project = load_project(ROOT / "examples" / "mini" / "project.yaml")
    registry = load_registry(ROOT / "registry" / "default.yaml")
    storyboard = generate_storyboard(project)

    prompt = compile_gpt_image_prompt(project, registry, storyboard)

    assert "2x3, 6-panel storyboard" in prompt
    assert "left-to-right, top-to-bottom" in prompt
    assert "crop-safe for 9:16" in prompt
    assert "only visual source of truth" in prompt
    assert "CONSISTENCY LOCK" in prompt
    assert "NEGATIVE CONSTRAINTS" in prompt
    assert "no subtitles" in prompt
    assert "no watermark" in prompt
    assert "no illegible text" in prompt
    for shot in storyboard.shots:
        assert f"{shot.id}. [{shot.purpose}]" in prompt
        assert shot.visual in prompt


def test_compile_prompt_is_deterministic():
    project = load_project(ROOT / "examples" / "mini" / "project.yaml")
    registry = load_registry(ROOT / "registry" / "default.yaml")
    storyboard = generate_storyboard(project)

    assert compile_gpt_image_prompt(
        project, registry, storyboard
    ) == compile_gpt_image_prompt(project, registry, storyboard)
