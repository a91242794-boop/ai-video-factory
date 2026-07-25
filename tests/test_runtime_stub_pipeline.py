from avf.runtime import (
    ExecutionContext,
    ModuleRegistry,
    ModuleRuntime,
    StubModule,
)


def test_default_stub_module_binds_through_runtime_io() -> None:
    registry = ModuleRegistry()
    registry.register(
        StubModule(
            module_id="stub",
            name="Stub",
            version="1.0.0",
        )
    )
    context = ExecutionContext(
        project_id="project-1",
        budget=0,
        quality_target=80,
        market="CN",
        locale="zh-CN",
    )

    outputs = ModuleRuntime(registry).execute(context)

    assert outputs["stub"].artifacts[0].artifact_id == "stub-output"
    assert outputs["stub"].cost == 0
