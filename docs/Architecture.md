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

## Capability-first execution

AVF describes production work by capability rather than model name. The four
initial capabilities are Director, Image Generation, Video Generation, and
Quality Assurance.

```text
Pipeline
  -> Capability Request
  -> Provider Router
  -> Adapter
  -> External Model
```

The Capability Layer implements stable request and result data, execution
metrics, and an in-memory registry of provider declarations. The Provider
Router selects an eligible declaration. The Adapter Execution Layer resolves
that provider ID to an Adapter and normalizes its response without coupling
the Router to provider execution.

The boundaries are intentionally distinct:

- a Contract defines what a module can do;
- a Capability Request expresses what this run needs;
- the Provider Router decides who should perform the work;
- an Adapter knows how to invoke and normalize one concrete tool or model.

Pipeline code depends on capability data rather than provider SDKs. This keeps
provider selection, fallback, and cost policy outside creative and workflow
logic. See [`Contracts.md`](Contracts.md) for the data-contract boundary.

## Adapter execution layer

The local execution boundary is:

```text
Capability Request
  -> Provider Router
  -> ProviderDescriptor
  -> AdapterRegistry
  -> Adapter
  -> CapabilityResult
```

`AdapterContract` defines the provider ID, capability, and `execute()` method.
`AdapterRegistry` stores executable Adapter instances separately from
`CapabilityRegistry`, which stores routing descriptions only. Matching
provider IDs connect selection to execution without making either registry
instantiate the other layer.

The current Director, Image, Video, and QA Adapters are deterministic local
Stubs. They return successful, provider-neutral results with zero estimated
cost, actual cost, and model tokens. They do not read credentials, access a
network, or invoke a real model.
