"""Zero-cost local module used to exercise the AVF runtime."""

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
        self._events = events

    def start(self) -> None:
        if self.state is ModuleState.RUNNING:
            return
        self.state = ModuleState.RUNNING
        self.start_count += 1
        if self._events is not None:
            self._events.append(f"start:{self.metadata.module_id}")

    def stop(self) -> None:
        if self.state is not ModuleState.RUNNING:
            return
        self.state = ModuleState.STOPPED
        self.stop_count += 1
        if self._events is not None:
            self._events.append(f"stop:{self.metadata.module_id}")
