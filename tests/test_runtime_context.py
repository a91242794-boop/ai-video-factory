from dataclasses import FrozenInstanceError

import pytest

from avf.runtime import ExecutionContext


def test_execution_context_preserves_runtime_inputs() -> None:
    context = ExecutionContext(
        project_id="project-1",
        budget=12.5,
        quality_target=85,
        market="CN",
        locale="zh-CN",
    )

    assert context.project_id == "project-1"
    assert context.budget == 12.5
    assert context.quality_target == 85
    assert context.market == "CN"
    assert context.locale == "zh-CN"
    with pytest.raises(FrozenInstanceError):
        context.budget = 20


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("project_id", " ", "project_id"),
        ("budget", -0.01, "budget"),
        ("quality_target", -1, "quality_target"),
        ("quality_target", 101, "quality_target"),
        ("market", " ", "market"),
        ("locale", " ", "locale"),
    ],
)
def test_execution_context_rejects_invalid_values(
    field: str,
    value: object,
    message: str,
) -> None:
    values: dict[str, object] = {
        "project_id": "project-1",
        "budget": 0,
        "quality_target": 80,
        "market": "CN",
        "locale": "zh-CN",
    }
    values[field] = value

    with pytest.raises(ValueError, match=message):
        ExecutionContext(**values)
