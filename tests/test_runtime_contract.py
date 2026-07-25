from avf.runtime import ModuleContract, ModuleMetadata, ModuleState


class ExampleModule:
    metadata = ModuleMetadata(
        module_id="example",
        name="Example Module",
        version="1.0.0",
    )
    state = ModuleState.CREATED

    def start(self) -> None:
        self.state = ModuleState.RUNNING

    def stop(self) -> None:
        self.state = ModuleState.STOPPED


def test_module_contract_supports_structural_runtime_checks() -> None:
    module = ExampleModule()

    assert isinstance(module, ModuleContract)
    assert module.metadata.module_id == "example"
    assert module.state is ModuleState.CREATED
