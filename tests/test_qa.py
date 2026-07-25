from dataclasses import replace
from pathlib import Path

from avf.compiler import compile_gpt_image_prompt
from avf.project import load_project
from avf.qa import run_static_qa
from avf.registry import load_registry
from avf.storyboard import generate_storyboard


ROOT = Path(__file__).parents[1]


def _valid_inputs():
    project = load_project(ROOT / "examples" / "mini" / "project.yaml")
    registry = load_registry(ROOT / "registry" / "default.yaml")
    storyboard = generate_storyboard(project)
    prompt = compile_gpt_image_prompt(project, registry, storyboard)
    return registry, storyboard, prompt


def test_static_qa_returns_passing_zero_token_report():
    registry, storyboard, prompt = _valid_inputs()

    report = run_static_qa(storyboard, prompt, registry)

    assert report["score"] == 100
    assert report["pass"] is True
    assert report["issues"] == []
    assert all(report["checks"].values())
    assert report["model_tokens_used"] == 0


def test_static_qa_reports_storyboard_failures():
    registry, storyboard, prompt = _valid_inputs()
    bad_shots = (
        replace(storyboard.shots[0], visual="duplicate"),
        replace(storyboard.shots[1], id=1, purpose="hook", visual="duplicate"),
        replace(storyboard.shots[2], purpose="problem", action=""),
        *storyboard.shots[3:5],
    )
    bad_storyboard = replace(storyboard, shots=bad_shots)

    report = run_static_qa(bad_storyboard, prompt, registry)

    assert report["pass"] is False
    assert report["score"] < registry.minimum_qa_score
    assert report["checks"]["shot_count"] is False
    assert report["checks"]["sequential_ids"] is False
    assert report["checks"]["purpose_sequence"] is False
    assert report["checks"]["product_reveal_by_shot_3"] is False
    assert report["checks"]["unique_visuals"] is False
    assert report["checks"]["required_fields"] is False
    assert report["issues"]


def test_static_qa_reports_prompt_failures():
    registry, storyboard, _ = _valid_inputs()
    incomplete_prompt = "\n".join(
        f"{shot.id}. [{shot.purpose}]" for shot in storyboard.shots[:5]
    )

    report = run_static_qa(storyboard, incomplete_prompt, registry)

    assert report["pass"] is False
    assert report["checks"]["prompt_has_all_shots"] is False
    assert report["checks"]["prompt_has_reference_lock"] is False
    assert report["checks"]["prompt_forbids_text"] is False
