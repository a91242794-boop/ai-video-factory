import json
import subprocess
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).parents[1]


def test_cli_run_writes_valid_pipeline_outputs(tmp_path):
    output = tmp_path / "mini"

    result = _run_cli(
        ROOT / "examples" / "mini" / "project.yaml",
        ROOT / "registry" / "default.yaml",
        output,
    )

    assert result.returncode == 0, result.stderr
    assert "QA PASS" in result.stdout
    storyboard = yaml.safe_load((output / "storyboard.yaml").read_text(encoding="utf-8"))
    prompt = (output / "gpt_image_prompt.md").read_text(encoding="utf-8")
    report = json.loads((output / "qa_report.json").read_text(encoding="utf-8"))
    assert len(storyboard["shots"]) == 6
    assert all(f"{shot_id}." in prompt for shot_id in range(1, 7))
    assert report["pass"] is True
    assert report["model_tokens_used"] == 0


def test_cli_returns_nonzero_when_qa_fails(tmp_path):
    registry = tmp_path / "registry.yaml"
    registry.write_text(
        """\
storyboard:
  purposes: [hook, problem, product_reveal, use, benefit, wrong]
compiler:
  target: gpt-image
qa:
  required_purposes: [hook, problem, product_reveal, use, benefit, wrong]
  minimum_score: 90
""",
        encoding="utf-8",
    )

    result = _run_cli(
        ROOT / "examples" / "mini" / "project.yaml",
        registry,
        tmp_path / "failed",
    )

    assert result.returncode == 1
    assert "QA FAIL" in result.stdout


def _run_cli(project: Path, registry: Path, output: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "avf.cli",
            "run",
            "--project",
            str(project),
            "--registry",
            str(registry),
            "--output",
            str(output),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
