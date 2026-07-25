# AVF Cost Strategy

AVF treats generation cost as a production constraint and a measurable business
input. The objective is not always to choose the cheapest provider; it is to
achieve the required quality at the lowest responsible total cost, including
retries and manual rework.

## Cost tiers

### Free first

Run deterministic, local, or already-paid checks before any metered model call.
Examples include project validation, Registry validation, storyboard
generation, prompt compilation, cache lookup, static QA, and artifact reuse.

Free-first steps must reject invalid work early and make the next paid action
more likely to succeed.

### Low cost

Use low-cost providers or configurations for exploration and low-risk
production steps:

- representative previews;
- draft images or short clips;
- low-resolution or reduced-sample validation;
- prompt and workflow experiments;
- revisions whose quality requirements are already well constrained.

Low-cost outputs must still meet the quality gate appropriate to their role.

### Premium

Use premium providers or settings only when the expected business value or
quality requirement justifies the higher cost. Typical cases include final
hero assets, packaging-sensitive product imagery, high-value campaigns, or a
failed lower-cost path with a documented reason to escalate.

Premium is an escalation tier, not the default.

## Provider priority

The AI Router evaluates eligible providers in this order:

1. capability fit for the requested artifact and constraints;
2. compliance, safety, and data-handling requirements;
3. expected quality and historical acceptance rate;
4. estimated total cost, including likely retries;
5. latency, availability, and quota;
6. project-specific provider preferences.

A cheaper provider is not preferred when it cannot satisfy a required
capability or quality gate.

## Fallback strategy

Fallbacks must be explicit, bounded, and observable.

1. Retry only transient failures within the configured attempt limit.
2. Reduce scope or regenerate only failed assets when partial work is valid.
3. Move to the next eligible provider in the same cost tier.
4. Escalate to a higher cost tier only with a recorded reason.
5. Stop and request operator review when no provider can meet the required
   constraints or the cost ceiling would be exceeded.

Fallback must never silently weaken compliance rules, product reference locks,
or required QA thresholds.

## Cost tracking

Each production run should record:

- project and run identifiers;
- module, provider, model, and configuration;
- estimated cost before execution;
- actual tokens, credits, media seconds, or billed units;
- currency and normalized cost;
- cache hits and reused artifacts;
- retry and fallback counts;
- accepted and rejected outputs;
- total cost per accepted deliverable.

Cost records should support provider comparison, budget enforcement, anomaly
detection, and business reporting. Missing provider cost data must be marked as
unknown rather than treated as zero.

## Capability routing policy

Free-first means lowest responsible cost, not unconditional selection of a
free model. The future Provider Router must first eliminate candidates that
cannot meet the request's minimum quality threshold. Among the remaining
eligible providers, it should choose the lowest expected total cost while
respecting exclusions, budget, latency, and capability fit.

If no free provider meets the quality threshold, routing should escalate to a
low-cost or paid provider. The reason and every fallback must be recorded.

Flow may be evaluated as a future free image-generation candidate. It is only
a candidate declaration until a tested Adapter exists; AVF does not currently
connect to or call Flow.

Every capability result should record `RunMetrics`: estimated cost, actual
cost, duration, quality score, fallback count, model tokens used, and cache-hit
status. Defaults of zero mean no measured usage in the local capability data
contract, not that unknown provider charges should be treated as free.
