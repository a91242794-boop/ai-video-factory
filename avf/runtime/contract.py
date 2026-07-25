"""Structural contract implemented by AVF runtime modules."""

from typing import Protocol, runtime_checkable

from avf.runtime.context import ExecutionContext
from avf.runtime.types import ModuleMetadata, ModuleState


@runtime_checkable
class ModuleContract(Protocol):
    metadata: ModuleMetadata
    state: ModuleState

    def initialize(self, context: ExecutionContext) -> None:
        """Prepare the module for execution."""
        ...

    def execute(self, context: ExecutionContext) -> object:
        """Execute local module work for one context."""
        ...

    def shutdown(self) -> None:
        """Release module resources."""
        ...

    def start(self) -> None:
        """Compatibility lifecycle entry point."""
        ...

    def stop(self) -> None:
        """Compatibility lifecycle exit point."""
        ...
