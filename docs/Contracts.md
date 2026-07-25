# AVF Contracts and Capabilities

AVF separates module interfaces from individual production requests so that
the pipeline can evolve without depending on a model vendor.

## Layer responsibilities

- **Contract** defines what an AVF module can do. The current Protocol
  interfaces cover directing, image generation, video generation, and quality
  assurance. They contain no provider implementation.
- **Capability Request** describes what a particular run needs, including the
  capability, project, cost, quality, speed, provider preferences, and
  capability-specific payload.
- **Provider Router** will decide who should perform the request. Router
  selection is planned for a later Sprint and is not implemented today.
- **Adapter** will define how AVF invokes a concrete tool or model and
  normalizes its response. No external model Adapter is currently included.

The intended dependency direction is:

```text
Pipeline
  -> Capability Request
  -> Provider Router
  -> Adapter
  -> External Model
```

The pipeline is capability-first, not model-first. It must not import a
provider SDK or construct provider-specific requests.

## Capability data contracts

AVF currently declares four stable capability values:

- `director`
- `image_generation`
- `video_generation`
- `quality_assurance`

Requests and results serialize to provider-neutral dictionaries. Every result
can carry `RunMetrics` for estimated and actual cost, duration, quality score,
fallback count, model token usage, and cache status.

`CapabilityRegistry` stores `ProviderDescriptor` declarations only. It neither
instantiates Adapters nor probes a network. A descriptor is not proof that a
provider is operational.
