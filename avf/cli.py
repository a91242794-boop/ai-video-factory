import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Sequence

import yaml

from avf.compiler import compile_gpt_image_prompt
from avf.project import ProjectError, load_project
from avf.qa import run_static_qa
from avf.registry import RegistryError, load_registry
from avf.storyboard import generate_storyboard


def run_pipeline(project_path: str, registry_path: str, output_path: str) -> int:
    project = load_project(project_path)
    registry = load_registry(registry_path)
    storyboard = generate_storyboard(project)
    prompt = compile_gpt_image_prompt(project, registry, storyboard)
    report = run_static_qa(storyboard, prompt, registry)

    output = Path(output_path)
    output.mkdir(parents=True, exist_ok=True)
    storyboard_data = asdict(storyboard)
    storyboard_data["shots"] = [dict(shot) for shot in storyboard_data["shots"]]
    (output / "storyboard.yaml").write_text(
        yaml.safe_dump(storyboard_data, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    (output / "gpt_image_prompt.md").write_text(prompt, encoding="utf-8")
    (output / "qa_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    status = "PASS" if report["pass"] else "FAIL"
    print(f"AVF Mini MVP: QA {status} ({report['score']}/100)")
    print(f"Output: {output}")
    return 0 if report["pass"] else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="avf")
    subparsers = parser.add_subparsers(dest="command", required=True)
    run = subparsers.add_parser("run", help="run the AVF Mini MVP pipeline")
    run.add_argument("--project", required=True)
    run.add_argument("--registry", required=True)
    run.add_argument("--output", required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "run":
            return run_pipeline(args.project, args.registry, args.output)
    except (ProjectError, RegistryError, OSError) as exc:
        print(f"AVF error: {exc}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
