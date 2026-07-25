"""In-memory registry for AVF runtime module instances."""

from avf.runtime.contract import ModuleContract


class ModuleRegistry:
    def __init__(self) -> None:
        self._modules: dict[str, ModuleContract] = {}

    def register(self, module: ModuleContract) -> None:
        module_id = module.metadata.module_id
        if module_id in self._modules:
            raise ValueError(f"Module already registered: {module_id}")
        self._modules[module_id] = module

    def get(self, module_id: str) -> ModuleContract:
        try:
            return self._modules[module_id]
        except KeyError as exc:
            raise KeyError(f"Unknown module: {module_id}") from exc

    def list(self) -> list[ModuleContract]:
        return sorted(
            self._modules.values(),
            key=lambda module: module.metadata.module_id,
        )

    def start_all(self) -> None:
        for module in self.list():
            module.start()

    def stop_all(self) -> None:
        for module in reversed(self.list()):
            module.stop()

    def clear(self) -> None:
        self._modules.clear()

    def __len__(self) -> int:
        return len(self._modules)
