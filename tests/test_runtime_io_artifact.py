from dataclasses import FrozenInstanceError

import pytest

from avf.runtime import Artifact


def test_artifact_is_typed_immutable_and_zero_cost() -> None:
    artifact = Artifact(
        artifact_id="storyboard-1",
        artifact_type="storyboard",
        data={"shots": 6},
        metadata={"source": "stub"},
    )

    assert artifact.artifact_id == "storyboard-1"
    assert artifact.artifact_type == "storyboard"
    assert artifact.data == {"shots": 6}
    assert artifact.metadata == {"source": "stub"}
    assert artifact.cost == 0
    with pytest.raises(FrozenInstanceError):
        artifact.cost = 1


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("artifact_id", " ", "artifact_id"),
        ("artifact_type", " ", "artifact_type"),
        ("cost", -0.01, "cost"),
        ("metadata", [], "metadata"),
    ],
)
def test_artifact_rejects_invalid_fields(
    field: str,
    value: object,
    message: str,
) -> None:
    values: dict[str, object] = {
        "artifact_id": "artifact-1",
        "artifact_type": "image",
        "data": b"stub",
    }
    values[field] = value

    with pytest.raises((TypeError, ValueError), match=message):
        Artifact(**values)


def test_artifact_rejects_non_artifact_metadata_keys() -> None:
    with pytest.raises(TypeError, match="metadata keys"):
        Artifact(
            artifact_id="artifact-1",
            artifact_type="image",
            data=b"stub",
            metadata={1: "invalid"},
        )
