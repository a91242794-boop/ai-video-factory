from avf.runtime import (
    ExecutionContext,
    ModuleContract,
    ModuleMetadata,
    ModuleState,
)


class ExampleModule:
    metadata = ModuleMetadata(
        module_id="example",
        name="Example Module",
        version="1.0.0",
    )
    state = ModuleState.CREATED

    def initialize(self, context: ExecutionContext) -> None:
        self.state = ModuleState.INITIALIZED

    def execute(self, context: ExecutionContext) -> object:
        self.state = ModuleState.RUNNING
        return {"project_id": context.project_id}

    def shutdown(self) -> None:
        self.state = ModuleState.STOPPED

    def start(self) -> None:
        self.state = ModuleState.RUNNING

    def stop(self) -> None:
        self.state = ModuleState.STOPPED


def test_module_contract_supports_structural_runtime_checks() -> None:
    module = ExampleModule()

    assert isinstance(module, ModuleContract)
    assert module.metadata.module_id == "example"
    assert module.state is ModuleState.CREATED
