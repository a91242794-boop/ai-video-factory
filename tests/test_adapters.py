import pytest

from avf.adapters import AdapterContract, AdapterRegistry
from avf.adapters.stub import (
    DirectorStubAdapter,
    ImageStubAdapter,
    QAStubAdapter,
    VideoStubAdapter,
)
from avf.capabilities.registry import (
    CapabilityRegistry,
    ProviderDescriptor,
)
from avf.capabilities.requests import (
    DirectorRequest,
    ImageGenerationRequest,
    QARequest,
    VideoGenerationRequest,
)
from avf.capabilities.types import (
    CapabilityType,
    CostTier,
    QualityTier,
    SpeedTier,
)
from avf.router import ProviderRouter


def test_adapter_registry_registers_queries_lists_and_clears() -> None:
    registry = AdapterRegistry()
    image = ImageStubAdapter()
    director = DirectorStubAdapter()

    registry.register(image)
    registry.register(director)

    assert registry.get(image.provider_id) is image
    assert [adapter.provider_id for adapter in registry.list()] == [
        director.provider_id,
        image.provider_id,
    ]
    assert registry.list(CapabilityType.IMAGE_GENERATION) == [image]
    assert isinstance(image, AdapterContract)

    registry.clear()

    assert registry.list() == []


def test_adapter_registry_rejects_duplicate_provider_id() -> None:
    registry = AdapterRegistry()
    registry.register(ImageStubAdapter())

    with pytest.raises(
        ValueError,
        match="Adapter already registered: stub-image",
    ):
        registry.register(ImageStubAdapter())


def test_router_selected_provider_can_execute_through_adapter_registry() -> None:
    providers = CapabilityRegistry()
    providers.register(
        ProviderDescriptor(
            provider_id="stub-image",
            capability=CapabilityType.IMAGE_GENERATION,
            cost_tier=CostTier.FREE,
            quality_tier=QualityTier.STANDARD,
            speed_tier=SpeedTier.FAST,
            priority=1,
            supports_free_tier=True,
        )
    )
    adapters = AdapterRegistry()
    adapters.register(ImageStubAdapter())
    request = ImageGenerationRequest(
        project_id="mini",
        storyboard={"shots": [1, 2, 3, 4, 5, 6]},
        reference_images=("product.png",),
    )

    descriptor = ProviderRouter(providers).select(request)
    result = adapters.get(descriptor.provider_id).execute(request)

    assert result.provider == descriptor.provider_id
    assert result.capability is CapabilityType.IMAGE_GENERATION
    assert result.success is True


@pytest.mark.parametrize(
    ("adapter", "capability_request"),
    [
        (
            DirectorStubAdapter(),
            DirectorRequest(
                project_id="mini",
                project_path="examples/mini/project.yaml",
            ),
        ),
        (
            ImageStubAdapter(),
            ImageGenerationRequest(
                project_id="mini",
                storyboard={"shots": []},
            ),
        ),
        (
            VideoStubAdapter(),
            VideoGenerationRequest(
                project_id="mini",
                storyboard={"shots": []},
                duration_seconds=15,
            ),
        ),
        (
            QAStubAdapter(),
            QARequest(
                project_id="mini",
                target_type="storyboard",
                payload={"shots": 6},
                minimum_score=85,
            ),
        ),
    ],
)
def test_stub_adapters_return_successful_zero_usage_results(
    adapter: AdapterContract,
    capability_request: object,
) -> None:
    result = adapter.execute(capability_request)
    serialized = result.to_dict()

    assert serialized["capability"] == adapter.capability.value
    assert serialized["provider"] == adapter.provider_id
    assert serialized["success"] is True
    assert isinstance(serialized["output"], dict)
    assert serialized["issues"] == []
    assert serialized["metrics"] == {
        "estimated_cost": 0,
        "actual_cost": 0,
        "duration_seconds": 0,
        "quality_score": None,
        "fallback_count": 0,
        "model_tokens_used": 0,
        "cache_hit": False,
    }
