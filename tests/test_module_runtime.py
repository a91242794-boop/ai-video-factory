import pytest

from avf.runtime import (
    ExecutionContext,
    ModuleDependency,
    ModuleRegistry,
    ModuleRuntime,
    ModuleState,
    StubModule,
)


def context() -> ExecutionContext:
    return ExecutionContext(
        project_id="project-1",
        budget=0,
        quality_target=85,
        market="CN",
        locale="zh-CN",
    )


def module(module_id: str, events: list[str]) -> StubModule:
    return StubModule(
        module_id=module_id,
        name=module_id.title(),
        version="1.0.0",
        events=events,
    )


def test_runtime_executes_modules_in_dependency_order() -> None:
    events: list[str] = []
    registry = ModuleRegistry()
    video = module("video", events)
    director = module("director", events)
    registry.register(video)
    registry.register(director)
    runtime = ModuleRuntime(
        registry,
        dependencies=(
            ModuleDependency(
                module_id="video",
                requires=("director",),
            ),
        ),
    )

    results = runtime.run(context())

    assert list(results) == ["director", "video"]
    assert results["director"]["cost"] == 0
    assert results["video"]["project_id"] == "project-1"
    assert events == [
        "initialize:director",
        "initialize:video",
        "execute:director",
        "execute:video",
        "shutdown:video",
        "shutdown:director",
    ]
    assert director.state is ModuleState.STOPPED
    assert video.state is ModuleState.STOPPED


def test_runtime_rejects_missing_dependency() -> None:
    registry = ModuleRegistry()
    registry.register(module("video", []))
    runtime = ModuleRuntime(
        registry,
        dependencies=(
            ModuleDependency(
                module_id="video",
                requires=("missing",),
            ),
        ),
    )

    with pytest.raises(ValueError, match="Unknown module dependency: missing"):
        runtime.run(context())


def test_runtime_rejects_dependency_cycles() -> None:
    registry = ModuleRegistry()
    registry.register(module("first", []))
    registry.register(module("second", []))
    runtime = ModuleRuntime(
        registry,
        dependencies=(
            ModuleDependency("first", requires=("second",)),
            ModuleDependency("second", requires=("first",)),
        ),
    )

    with pytest.raises(ValueError, match="cycle"):
        runtime.run(context())


def test_runtime_shuts_down_initialized_modules_after_failure() -> None:
    events: list[str] = []

    class FailingStubModule(StubModule):
        def execute(self, execution_context: ExecutionContext) -> object:
            super().execute(execution_context)
            raise RuntimeError("stub failure")

    registry = ModuleRegistry()
    first = module("first", events)
    failing = FailingStubModule(
        module_id="failing",
        name="Failing",
        version="1.0.0",
        events=events,
    )
    registry.register(first)
    registry.register(failing)

    with pytest.raises(RuntimeError, match="stub failure"):
        ModuleRuntime(registry).run(context())

    assert first.state is ModuleState.STOPPED
    assert failing.state is ModuleState.STOPPED
    assert events[-2:] == ["shutdown:first", "shutdown:failing"]
