from avf.runtime import (
    Artifact,
    ExecutionContext,
    ModuleInput,
    ModuleOutput,
    ModuleRegistry,
    ModuleRuntime,
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


class PipelineStub(StubModule):
    def execute_io(self, module_input: ModuleInput) -> ModuleOutput:
        self.execute(module_input.context)
        input_ids = [item.artifact_id for item in module_input.artifacts]
        return ModuleOutput(
            artifacts=(
                Artifact(
                    artifact_id=f"{self.metadata.module_id}-output",
                    artifact_type="stub-output",
                    data=input_ids,
                    metadata={"module_id": self.metadata.module_id},
                ),
            ),
        )


def test_runtime_execute_binds_io_and_persists_artifacts() -> None:
    registry = ModuleRegistry()
    registry.register(
        PipelineStub(
            module_id="first",
            name="First",
            version="1.0.0",
        )
    )
    registry.register(
        PipelineStub(
            module_id="second",
            name="Second",
            version="1.0.0",
        )
    )
    runtime = ModuleRuntime(registry)
    initial = Artifact(
        artifact_id="initial",
        artifact_type="input",
        data="seed",
    )

    outputs = runtime.execute(
        context(),
        ModuleInput(artifacts=(initial,), context=context()),
    )

    assert list(outputs) == ["first", "second"]
    assert outputs["first"].artifacts[0].data == ["initial"]
    assert outputs["second"].artifacts[0].data == [
        "first-output",
        "initial",
    ]
    assert [item.artifact_id for item in runtime.artifact_store.list()] == [
        "first-output",
        "initial",
        "second-output",
    ]
    assert all(output.cost == 0 for output in outputs.values())


def test_runtime_execute_accepts_context_without_explicit_input() -> None:
    registry = ModuleRegistry()
    registry.register(
        PipelineStub(
            module_id="stub",
            name="Stub",
            version="1.0.0",
        )
    )

    outputs = ModuleRuntime(registry).execute(context())

    assert outputs["stub"].artifacts[0].data == []
