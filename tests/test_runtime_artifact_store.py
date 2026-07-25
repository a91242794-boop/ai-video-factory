import pytest

from avf.runtime import Artifact, ArtifactStore


def artifact(artifact_id: str) -> Artifact:
    return Artifact(
        artifact_id=artifact_id,
        artifact_type="stub",
        data=artifact_id,
    )


def test_artifact_store_put_get_list_and_clear() -> None:
    store = ArtifactStore()
    second = artifact("second")
    first = artifact("first")

    store.put(second)
    store.put(first)

    assert len(store) == 2
    assert store.get("first") is first
    assert store.list() == [first, second]

    store.clear()

    assert len(store) == 0
    assert store.list() == []


def test_artifact_store_rejects_duplicate_and_unknown_artifacts() -> None:
    store = ArtifactStore()
    store.put(artifact("duplicate"))

    with pytest.raises(ValueError, match="Artifact already stored"):
        store.put(artifact("duplicate"))
    with pytest.raises(KeyError, match="Unknown artifact: missing"):
        store.get("missing")


def test_artifact_store_rejects_non_artifact_values() -> None:
    with pytest.raises(TypeError, match="Artifact"):
        ArtifactStore().put("not-an-artifact")
