import pytest

from avf.runtime import (
    ModuleMetadata,
    ModuleRegistry,
    ModuleState,
)


class RegistryModule:
    def __init__(self, module_id: str) -> None:
        self.metadata = ModuleMetadata(
            module_id=module_id,
            name=module_id,
            version="1.0.0",
        )
        self.state = ModuleState.CREATED

    def start(self) -> None:
        self.state = ModuleState.RUNNING

    def stop(self) -> None:
        self.state = ModuleState.STOPPED


def test_module_registry_registers_queries_lists_and_clears() -> None:
    registry = ModuleRegistry()
    second = RegistryModule("second")
    first = RegistryModule("first")

    registry.register(second)
    registry.register(first)

    assert len(registry) == 2
    assert registry.get("first") is first
    assert registry.list() == [first, second]

    registry.clear()

    assert len(registry) == 0
    assert registry.list() == []


def test_module_registry_rejects_duplicate_ids() -> None:
    registry = ModuleRegistry()
    registry.register(RegistryModule("duplicate"))

    with pytest.raises(
        ValueError,
        match="Module already registered: duplicate",
    ):
        registry.register(RegistryModule("duplicate"))


def test_module_registry_reports_unknown_ids() -> None:
    with pytest.raises(KeyError, match="Unknown module: missing"):
        ModuleRegistry().get("missing")
