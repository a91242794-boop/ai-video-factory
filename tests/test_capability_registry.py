import pytest

from avf.capabilities.registry import (
    CapabilityRegistry,
    ProviderDescriptor,
)
from avf.capabilities.types import (
    CapabilityType,
    CostTier,
    QualityTier,
    SpeedTier,
)


def descriptor(
    provider_id: str,
    *,
    capability: CapabilityType = CapabilityType.IMAGE_GENERATION,
    enabled: bool = True,
    priority: int = 100,
) -> ProviderDescriptor:
    return ProviderDescriptor(
        provider_id=provider_id,
        capability=capability,
        cost_tier=CostTier.FREE,
        quality_tier=QualityTier.STANDARD,
        speed_tier=SpeedTier.BALANCED,
        enabled=enabled,
        priority=priority,
        supports_free_tier=True,
    )


def test_registry_registers_and_gets_descriptor() -> None:
    registry = CapabilityRegistry()
    item = descriptor("example")

    registry.register(item)

    assert len(registry) == 1
    assert registry.get("example") is item


def test_registry_rejects_duplicate_provider_id() -> None:
    registry = CapabilityRegistry()
    registry.register(descriptor("duplicate"))

    with pytest.raises(
        ValueError,
        match="Provider already registered: duplicate",
    ):
        registry.register(
            descriptor(
                "duplicate",
                capability=CapabilityType.VIDEO_GENERATION,
            )
        )


def test_registry_get_reports_unknown_provider() -> None:
    registry = CapabilityRegistry()

    with pytest.raises(KeyError, match="Unknown provider: missing"):
        registry.get("missing")


def test_registry_filters_by_capability_and_enabled_state() -> None:
    registry = CapabilityRegistry()
    registry.register(descriptor("image-enabled"))
    registry.register(descriptor("image-disabled", enabled=False))
    registry.register(
        descriptor(
            "video-enabled",
            capability=CapabilityType.VIDEO_GENERATION,
        )
    )

    assert [
        item.provider_id
        for item in registry.list_for(CapabilityType.IMAGE_GENERATION)
    ] == ["image-enabled"]
    assert [
        item.provider_id
        for item in registry.list_for(
            CapabilityType.IMAGE_GENERATION,
            enabled_only=False,
        )
    ] == ["image-disabled", "image-enabled"]


def test_registry_sorts_by_priority_then_provider_id() -> None:
    registry = CapabilityRegistry()
    registry.register(descriptor("z-last", priority=20))
    registry.register(descriptor("b-second", priority=10))
    registry.register(descriptor("a-first", priority=10))

    assert [
        item.provider_id
        for item in registry.list_for(CapabilityType.IMAGE_GENERATION)
    ] == ["a-first", "b-second", "z-last"]


def test_registry_clear_removes_all_descriptors() -> None:
    registry = CapabilityRegistry()
    registry.register(descriptor("example"))

    registry.clear()

    assert len(registry) == 0
    assert registry.list_for(CapabilityType.IMAGE_GENERATION) == []
