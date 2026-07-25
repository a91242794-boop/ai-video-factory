"""In-memory storage for provider-neutral module artifacts."""

from avf.runtime.io import Artifact


class ArtifactStore:
    def __init__(self) -> None:
        self._artifacts: dict[str, Artifact] = {}

    def put(self, artifact: Artifact) -> None:
        if not isinstance(artifact, Artifact):
            raise TypeError("ArtifactStore accepts only Artifact values")
        if artifact.artifact_id in self._artifacts:
            raise ValueError(
                f"Artifact already stored: {artifact.artifact_id}"
            )
        self._artifacts[artifact.artifact_id] = artifact

    def get(self, artifact_id: str) -> Artifact:
        try:
            return self._artifacts[artifact_id]
        except KeyError as exc:
            raise KeyError(f"Unknown artifact: {artifact_id}") from exc

    def list(self) -> list[Artifact]:
        return sorted(
            self._artifacts.values(),
            key=lambda artifact: artifact.artifact_id,
        )

    def clear(self) -> None:
        self._artifacts.clear()

    def __len__(self) -> int:
        return len(self._artifacts)
