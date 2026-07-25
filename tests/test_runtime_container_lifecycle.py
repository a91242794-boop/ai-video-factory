import pytest

from avf.runtime import (
    ExecutionContext,
    ModuleState,
    StubModule,
)


def context() -> ExecutionContext:
    return ExecutionContext(
        project_id="project-1",
        budget=0,
        quality_target=80,
        market="CN",
        locale="zh-CN",
    )


def test_stub_module_follows_container_lifecycle() -> None:
    events: list[str] = []
    module = StubModule(
        module_id="stub-runtime",
        name="Stub Runtime",
        version="1.0.0",
        events=events,
    )

    module.initialize(context())
    assert module.state is ModuleState.INITIALIZED

    result = module.execute(context())
    assert module.state is ModuleState.RUNNING
    assert result == {
        "module_id": "stub-runtime",
        "project_id": "project-1",
        "cost": 0,
        "stub": True,
    }

    module.shutdown()
    assert module.state is ModuleState.STOPPED
    assert events == [
        "initialize:stub-runtime",
        "execute:stub-runtime",
        "shutdown:stub-runtime",
    ]


def test_stub_module_rejects_execute_before_initialize() -> None:
    module = StubModule(
        module_id="stub-runtime",
        name="Stub Runtime",
        version="1.0.0",
    )

    with pytest.raises(RuntimeError, match="must be initialized"):
        module.execute(context())
