"""Public API for the modular AVF runtime foundation."""

from avf.runtime.container import ModuleRuntime
from avf.runtime.context import ExecutionContext
from avf.runtime.contract import ModuleContract
from avf.runtime.dependency import ModuleDependency
from avf.runtime.registry import ModuleRegistry
from avf.runtime.stub import StubModule
from avf.runtime.types import ModuleMetadata, ModuleState

__all__ = [
    "ExecutionContext",
    "ModuleContract",
    "ModuleDependency",
    "ModuleMetadata",
    "ModuleRegistry",
    "ModuleRuntime",
    "ModuleState",
    "StubModule",
]
