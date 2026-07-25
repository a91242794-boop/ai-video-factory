# AVF Architecture

AVF uses a modular production architecture coordinated by AVF OS. Each module
owns a focused responsibility and communicates through stable project,
artifact, and QA contracts.

## AVF OS

AVF OS is the orchestration layer. It loads project configuration, resolves the
workflow, coordinates modules, applies quality and cost policies, and records
run state. It does not contain provider-specific generation logic or creative
decisions that belong to specialist modules.

Core responsibilities:

- project and Registry loading;
- workflow sequencing and state transitions;
- artifact lineage and run status;
- quality-gate enforcement;
- retry, resume, and failure handling;
- delegation to the AI Router and Production Manager.

The current Mini MVP CLI is the first local orchestration surface for this
layer.

## Director Module

The Director Module converts business goals, audience context, product facts,
and creative constraints into a production-ready narrative plan. It owns the
commercial concept, hook, message sequence, CTA intent, and shot purposes. It
does not render media or make provider-routing decisions.

## Image Module

The Image Module converts approved visual specifications and reference locks
into image-generation requests and normalized image artifacts. It is
responsible for prompt preparation, reference packaging, image-provider
adapters, and image metadata. It must preserve product and brand constraints
defined by upstream contracts.

The Mini MVP prompt compiler provides the deterministic prompt-preparation
portion of this boundary; external image generation is not yet implemented.

## Video Module

The Video Module converts approved shots and media references into video
generation or assembly requests. It owns motion instructions, duration,
transitions, clip metadata, and video-provider adapters. It consumes approved
creative and visual inputs without redefining their business intent.

External video generation is outside the current Mini MVP.

## QA Module

The QA Module evaluates projects, prompts, images, clips, and final
deliverables against explicit rules and thresholds. It produces structured QA
reports containing scores, pass status, checks, and actionable issues.

Static checks should run before model-assisted or human QA. A failed required
gate stops downstream production or triggers a bounded revision path.

## AI Router

The AI Router selects an eligible model provider and configuration for a
requested capability. Routing considers capability fit, policy, expected
quality, cost tier, historical performance, availability, and project
preferences.

Provider implementations remain adapters behind this boundary. Modules request
a capability and receive a normalized result; they do not embed vendor
credentials or routing policy. Routing follows
[`CostStrategy.md`](CostStrategy.md).

## Production Manager

The Production Manager tracks the operational lifecycle of a production run:
planned work, queued tasks, active attempts, artifacts, approvals, failures,
cost, and delivery status. It coordinates retries and fallbacks with AVF OS
while preserving accepted work.

The Production Manager is responsible for observability and operational state,
not creative generation or QA scoring.

## Module flow

```text
Project + Registry
        |
        v
      AVF OS
        |
        +--> Director Module
        |
        +--> AI Router --> Image Module / Video Module
        |
        +--> QA Module
        |
        +--> Production Manager
        |
        v
Approved, traceable production artifacts
```

All module boundaries follow the principles in
[`ProductPrinciples.md`](ProductPrinciples.md): business efficiency first,
cost-aware generation, model independence, modularity, and quality-controlled
automation.
