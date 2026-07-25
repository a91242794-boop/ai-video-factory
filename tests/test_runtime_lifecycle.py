from avf.runtime import (
    ModuleContract,
    ModuleRegistry,
    ModuleState,
    StubModule,
)


def test_stub_module_has_zero_cost_idempotent_lifecycle() -> None:
    module = StubModule(
        module_id="stub-runtime",
        name="Stub Runtime",
        version="1.0.0",
    )

    assert isinstance(module, ModuleContract)
    assert module.metadata.cost == 0
    assert module.state is ModuleState.CREATED

    module.start()
    module.start()

    assert module.state is ModuleState.RUNNING
    assert module.start_count == 1

    module.stop()
    module.stop()

    assert module.state is ModuleState.STOPPED
    assert module.stop_count == 1


def test_registry_starts_and_stops_all_modules_deterministically() -> None:
    events: list[str] = []
    registry = ModuleRegistry()
    second = StubModule(
        module_id="second",
        name="Second",
        version="1.0.0",
        events=events,
    )
    first = StubModule(
        module_id="first",
        name="First",
        version="1.0.0",
        events=events,
    )
    registry.register(second)
    registry.register(first)

    registry.start_all()
    registry.stop_all()

    assert events == [
        "start:first",
        "start:second",
        "stop:second",
        "stop:first",
    ]
    assert first.state is ModuleState.STOPPED
    assert second.state is ModuleState.STOPPED
