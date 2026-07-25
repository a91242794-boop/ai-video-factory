import pytest

from avf.runtime import (
    Artifact,
    ExecutionContext,
    ModuleExecutor,
    ModuleInput,
    ModuleOutput,
)


def context() -> ExecutionContext:
    return ExecutionContext(
        project_id="project-1",
        budget=0,
        quality_target=80,
        market="CN",
        locale="zh-CN",
    )


class IOAwareModule:
    def __init__(self) -> None:
        self.received: ModuleInput | None = None

    def execute_io(self, module_input: ModuleInput) -> ModuleOutput:
        self.received = module_input
        return ModuleOutput(
            artifacts=(
                Artifact(
                    artifact_id="output-1",
                    artifact_type="stub",
                    data=module_input.context.project_id,
                ),
            ),
        )


class LegacyModule:
    def __init__(self) -> None:
        self.received: ExecutionContext | None = None

    def execute(self, execution_context: ExecutionContext) -> dict[str, str]:
        self.received = execution_context
        return {"status": "legacy"}


def test_module_executor_binds_module_input_to_io_aware_module() -> None:
    module = IOAwareModule()
    module_input = ModuleInput(context=context())

    output = ModuleExecutor().execute(module, module_input)

    assert module.received is module_input
    assert isinstance(output, ModuleOutput)
    assert output.artifacts[0].artifact_id == "output-1"
    assert output.cost == 0


def test_module_executor_wraps_legacy_module_output() -> None:
    module = LegacyModule()

    output = ModuleExecutor().execute(
        module,
        ModuleInput(context=context()),
    )

    assert module.received is not None
    assert module.received.project_id == "project-1"
    assert output == ModuleOutput(metadata={"result": {"status": "legacy"}})


def test_module_executor_requires_context_for_legacy_module() -> None:
    with pytest.raises(ValueError, match="context"):
        ModuleExecutor().execute(LegacyModule(), ModuleInput())
