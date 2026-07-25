import pytest

from avf.runtime import (
    Artifact,
    ExecutionContext,
    ModuleInput,
    ModuleOutput,
)


def execution_context() -> ExecutionContext:
    return ExecutionContext(
        project_id="project-1",
        budget=0,
        quality_target=80,
        market="CN",
        locale="zh-CN",
    )


def artifact(artifact_id: str = "input-1") -> Artifact:
    return Artifact(
        artifact_id=artifact_id,
        artifact_type="text",
        data="stub",
    )


def test_module_input_normalizes_artifacts_and_keeps_context() -> None:
    module_input = ModuleInput(
        artifacts=[artifact()],
        context=execution_context(),
    )

    assert module_input.artifacts == (artifact(),)
    assert module_input.context is not None
    assert module_input.context.project_id == "project-1"


def test_module_output_normalizes_artifacts_and_defaults_to_zero_cost() -> None:
    module_output = ModuleOutput(
        artifacts=[artifact("output-1")],
        metadata={"status": "stub"},
    )

    assert module_output.artifacts == (artifact("output-1"),)
    assert module_output.metadata == {"status": "stub"}
    assert module_output.cost == 0


@pytest.mark.parametrize("value", [None, ["not-an-artifact"], "artifact"])
def test_module_input_rejects_invalid_artifacts(value: object) -> None:
    with pytest.raises(TypeError, match="artifacts"):
        ModuleInput(artifacts=value)


@pytest.mark.parametrize("value", [None, ["not-an-artifact"], "artifact"])
def test_module_output_rejects_invalid_artifacts(value: object) -> None:
    with pytest.raises(TypeError, match="artifacts"):
        ModuleOutput(artifacts=value)


def test_module_output_rejects_invalid_metadata_and_cost() -> None:
    with pytest.raises(TypeError, match="metadata"):
        ModuleOutput(artifacts=(), metadata=[])
    with pytest.raises(ValueError, match="cost"):
        ModuleOutput(artifacts=(), cost=-1)
