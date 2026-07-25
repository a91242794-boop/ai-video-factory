"""Structural contract implemented by AVF runtime modules."""

from typing import Protocol, runtime_checkable

from avf.runtime.types import ModuleMetadata, ModuleState


@runtime_checkable
class ModuleContract(Protocol):
    metadata: ModuleMetadata
    state: ModuleState

    def start(self) -> None:
        """Start the module."""
        ...

    def stop(self) -> None:
        """Stop the module."""
        ...
