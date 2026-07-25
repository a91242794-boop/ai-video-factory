# AVF Product Principles

AI Video Factory (AVF) is a business-efficiency-first AI video production
system. Product decisions should improve the speed, cost, reliability, and
commercial usefulness of producing video assets.

## Business Efficiency First

AVF optimizes for useful business outcomes rather than maximum generation
volume or technical novelty. A workflow should reduce production time, manual
coordination, or avoidable rework while producing assets that serve a defined
audience, channel, and commercial goal.

- Start from a structured project brief and an explicit delivery target.
- Prefer deterministic local processing before model calls.
- Generate only the assets needed to make or validate the next decision.
- Make failures actionable so teams can correct the smallest possible scope.
- Measure success through production throughput, acceptance rate, cost, and
  business usability.

## Cost-Aware Generation

Every generation step must have a clear reason, expected value, and cost tier.
AVF should validate structure and constraints locally before spending model
tokens or generation credits.

- Use free validation and compilation before paid generation.
- Preview high-risk decisions before producing full deliverables.
- Reuse valid inputs and outputs instead of regenerating unchanged work.
- Escalate to more expensive models only when quality requirements justify it.
- Record estimated and actual costs at the project, run, and provider levels.

The detailed provider and fallback policy is defined in
[`CostStrategy.md`](CostStrategy.md).

## Modular Architecture

AVF is composed of small modules with explicit inputs, outputs, and ownership.
Modules should be independently testable and replaceable without requiring
unrelated workflow changes.

- Domain models define stable contracts between modules.
- Orchestration coordinates modules but does not absorb their business logic.
- Provider-specific behavior stays behind module or adapter boundaries.
- QA gates remain separate from generation so quality policy can evolve
  independently.
- Generated artifacts retain enough metadata to trace their source and status.

The module map and responsibilities are defined in
[`Architecture.md`](Architecture.md).

## Model Independence

AVF workflows must not depend on one model vendor, API, or generation engine.
Projects, storyboards, prompts, QA reports, and production state remain
provider-neutral wherever possible.

- The AI Router selects providers according to capability, policy, cost, and
  availability.
- Provider adapters translate stable AVF contracts into provider requests.
- A provider failure should not corrupt the project or erase valid artifacts.
- Model upgrades should not require changes to unrelated business modules.
- Model-specific features are optional capabilities, not assumptions embedded
  across the system.

## Quality Controlled Automation

Automation is allowed to proceed only through explicit quality gates. AVF
combines deterministic validation, static QA, model-assisted QA where
appropriate, and human review for high-risk decisions.

- Validate required fields and workflow invariants before generation.
- Use measurable checks with clear pass thresholds and issue codes.
- Stop or return a non-zero status when required quality is not met.
- Preserve accepted work and revise only failed or affected assets.
- Keep a traceable record of checks, decisions, retries, and final acceptance.

Automation should reduce repetitive work without hiding uncertainty or
removing necessary human accountability.
