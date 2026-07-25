"""Dependency-aware lifecycle container for AVF runtime modules."""

from collections.abc import Iterable

from avf.runtime.context import ExecutionContext
from avf.runtime.contract import ModuleContract
from avf.runtime.dependency import ModuleDependency
from avf.runtime.executor import ModuleExecutor
from avf.runtime.io import ModuleInput, ModuleOutput
from avf.runtime.registry import ModuleRegistry
from avf.runtime.store import ArtifactStore


class ModuleRuntime:
    def __init__(
        self,
        registry: ModuleRegistry,
        *,
        dependencies: Iterable[ModuleDependency] = (),
        executor: ModuleExecutor | None = None,
        artifact_store: ArtifactStore | None = None,
    ) -> None:
        self._registry = registry
        self._dependencies = tuple(dependencies)
        self._executor = executor or ModuleExecutor()
        self.artifact_store = artifact_store or ArtifactStore()

    def run(self, context: ExecutionContext) -> dict[str, object]:
        modules = self._ordered_modules()
        initialized: list[ModuleContract] = []
        results: dict[str, object] = {}
        try:
            for module in modules:
                module.initialize(context)
                initialized.append(module)
            for module in modules:
                results[module.metadata.module_id] = module.execute(
                    context
                )
            return results
        finally:
            for module in reversed(initialized):
                module.shutdown()

    def execute(
        self,
        context: ExecutionContext,
        module_input: ModuleInput | None = None,
    ) -> dict[str, ModuleOutput]:
        if not isinstance(context, ExecutionContext):
            raise TypeError("context must be an ExecutionContext")
        if module_input is not None and not isinstance(
            module_input, ModuleInput
        ):
            raise TypeError("module_input must be a ModuleInput")

        input_artifacts = () if module_input is None else module_input.artifacts
        self.artifact_store.clear()
        for artifact in input_artifacts:
            self.artifact_store.put(artifact)

        modules = self._ordered_modules()
        initialized: list[ModuleContract] = []
        outputs: dict[str, ModuleOutput] = {}
        try:
            for module in modules:
                module.initialize(context)
                initialized.append(module)
            for module in modules:
                bound_input = ModuleInput(
                    artifacts=tuple(self.artifact_store.list()),
                    context=context,
                )
                output = self._executor.execute(module, bound_input)
                outputs[module.metadata.module_id] = output
                for artifact in output.artifacts:
                    self.artifact_store.put(artifact)
            return outputs
        finally:
            for module in reversed(initialized):
                module.shutdown()

    def _ordered_modules(self) -> list[ModuleContract]:
        modules = {
            module.metadata.module_id: module
            for module in self._registry.list()
        }
        requirements: dict[str, tuple[str, ...]] = {
            module_id: () for module_id in modules
        }
        for dependency in self._dependencies:
            if dependency.module_id not in modules:
                raise ValueError(
                    f"Unknown runtime module: {dependency.module_id}"
                )
            if requirements[dependency.module_id]:
                raise ValueError(
                    f"Duplicate dependency description: "
                    f"{dependency.module_id}"
                )
            for required_id in dependency.requires:
                if required_id not in modules:
                    raise ValueError(
                        f"Unknown module dependency: {required_id}"
                    )
            requirements[dependency.module_id] = dependency.requires

        ordered_ids: list[str] = []
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(module_id: str) -> None:
            if module_id in visiting:
                raise ValueError(
                    f"Module dependency cycle detected: {module_id}"
                )
            if module_id in visited:
                return
            visiting.add(module_id)
            for required_id in sorted(requirements[module_id]):
                visit(required_id)
            visiting.remove(module_id)
            visited.add(module_id)
            ordered_ids.append(module_id)

        for module_id in sorted(modules):
            visit(module_id)
        return [modules[module_id] for module_id in ordered_ids]
