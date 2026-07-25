"""Compatibility-aware executor for module IO bindings."""

from avf.runtime.context import ExecutionContext
from avf.runtime.io import ModuleInput, ModuleOutput


class ModuleExecutor:
    def execute(
        self,
        module: object,
        module_input: ModuleInput,
    ) -> ModuleOutput:
        if not isinstance(module_input, ModuleInput):
            raise TypeError("module_input must be a ModuleInput")

        execute_io = getattr(module, "execute_io", None)
        if callable(execute_io):
            output = execute_io(module_input)
        else:
            context = module_input.context
            if not isinstance(context, ExecutionContext):
                raise ValueError(
                    "ModuleInput context is required for legacy modules"
                )
            execute = getattr(module, "execute", None)
            if not callable(execute):
                raise TypeError("module must expose execute or execute_io")
            output = execute(context)

        if isinstance(output, ModuleOutput):
            return output
        if isinstance(output, dict):
            return ModuleOutput(metadata={"result": output})
        raise TypeError("module execution must return ModuleOutput or dict")
