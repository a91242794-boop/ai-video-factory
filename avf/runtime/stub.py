"""Zero-cost local module used to exercise the AVF runtime."""

from avf.runtime.context import ExecutionContext
from avf.runtime.io import Artifact, ModuleInput, ModuleOutput
from avf.runtime.types import ModuleMetadata, ModuleState


class StubModule:
    def __init__(
        self,
        *,
        module_id: str,
        name: str,
        version: str,
        events: list[str] | None = None,
    ) -> None:
        self.metadata = ModuleMetadata(
            module_id=module_id,
            name=name,
            version=version,
        )
        self.state = ModuleState.CREATED
        self.start_count = 0
        self.stop_count = 0
        self.initialize_count = 0
        self.execute_count = 0
        self.shutdown_count = 0
        self._events = events

    def initialize(self, context: ExecutionContext) -> None:
        if self.state in (
            ModuleState.INITIALIZED,
            ModuleState.RUNNING,
        ):
            return
        self.state = ModuleState.INITIALIZED
        self.initialize_count += 1
        self._record("initialize")

    def execute(self, context: ExecutionContext) -> object:
        if self.state not in (
            ModuleState.INITIALIZED,
            ModuleState.RUNNING,
        ):
            raise RuntimeError(
                f"Module must be initialized before execute: "
                f"{self.metadata.module_id}"
            )
        self.state = ModuleState.RUNNING
        self.execute_count += 1
        self._record("execute")
        return {
            "module_id": self.metadata.module_id,
            "project_id": context.project_id,
            "cost": self.metadata.cost,
            "stub": True,
        }

    def execute_io(self, module_input: ModuleInput) -> ModuleOutput:
        if not isinstance(module_input.context, ExecutionContext):
            raise ValueError("ModuleInput context is required")
        self.execute(module_input.context)
        return ModuleOutput(
            artifacts=(
                Artifact(
                    artifact_id=f"{self.metadata.module_id}-output",
                    artifact_type="stub-output",
                    data={
                        "project_id": module_input.context.project_id,
                        "input_count": len(module_input.artifacts),
                    },
                ),
            ),
            metadata={"module_id": self.metadata.module_id},
        )

    def shutdown(self) -> None:
        if self.state in (ModuleState.CREATED, ModuleState.STOPPED):
            return
        self.state = ModuleState.STOPPED
        self.shutdown_count += 1
        self._record("shutdown")

    def start(self) -> None:
        if self.state is ModuleState.RUNNING:
            return
        self.state = ModuleState.RUNNING
        self.start_count += 1
        self._record("start")

    def stop(self) -> None:
        if self.state is not ModuleState.RUNNING:
            return
        self.state = ModuleState.STOPPED
        self.stop_count += 1
        self._record("stop")

    def _record(self, action: str) -> None:
        if self._events is not None:
            self._events.append(
                f"{action}:{self.metadata.module_id}"
            )
