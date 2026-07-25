# AI Video Factory Mini MVP

**AVF positioning:** Business efficiency first AI video production system.

AVF Mini MVP is a deterministic, local pipeline that turns a validated product
project into a six-shot storyboard, a GPT Image storyboard prompt, and a static
QA report. It does not call an LLM, image model, network API, or other external
service.

## Features

- Validated `project.yaml` input with a fixed six-shot contract.
- Registry-configured shot purposes, compiler target, and QA threshold.
- Deterministic hook, problem, product reveal, use, benefit, and CTA sequence.
- A 2x3 GPT Image prompt with 9:16-safe panels, reference locks, continuity,
  and negative constraints.
- Zero-token static QA with a machine-readable JSON report.
- CLI exit code `0` for QA pass, `1` for QA failure, and `2` for input errors.

## Install

Python 3.11 or newer is required.

```bash
python -m pip install -e ".[dev]"
```

## Quick start

```bash
python -m avf.cli run \
  --project examples/mini/project.yaml \
  --registry registry/default.yaml \
  --output outputs/mini
```

After installation, `avf run` accepts the same arguments.

## Project input

`project.yaml` requires these sections and fields:

- `project`: `id`, `name`
- `product`: `name`, `category`, non-empty `key_features`, non-empty `reference_images`
- `market`: `country`, `language`, `platform`, `audience`
- `video`: positive `duration_seconds`, `shot_count: 6`, `aspect_ratio`
- `creative`: `hook`, `tone`, `environment`, `character`, `cta`

YAML mappings must not contain duplicate keys. The Mini MVP rejects incomplete,
ambiguous, or internally inconsistent project and Registry files before writing
outputs. See `examples/mini/project.yaml` and `registry/default.yaml` for complete
working examples.

## Exit codes

- `0`: pipeline completed and QA passed.
- `1`: pipeline completed and QA failed; diagnostic outputs were written.
- `2`: project, Registry, path, or runtime input error.

## Outputs

- `storyboard.yaml`: exactly six deterministic shots.
- `gpt_image_prompt.md`: a model-ready 2x3 storyboard prompt.
- `qa_report.json`: score, pass status, issues, checks, and zero model tokens.

Generated output files are ignored by Git; `outputs/.gitkeep` preserves the
directory.

## Tests

```bash
python -m pytest -v
```

Each stage can also be run through its matching file in `tests/`.

## Current limitations

- Exactly six shots and one deterministic creative template are supported.
- Reference paths are embedded in the prompt but images are not opened or
  visually verified.
- QA checks structure and prompt content, not generated imagery.
- The pipeline compiles a prompt but never invokes GPT Image or an external
  model.
