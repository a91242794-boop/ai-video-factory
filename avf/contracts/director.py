"""Contract for storyboard direction."""

from typing import Protocol

from avf.models import Project
from avf.registry import Registry
from avf.storyboard_models import Storyboard


class DirectorContract(Protocol):
    """Create a storyboard without prescribing a concrete director."""

    def create_storyboard(
        self,
        project: Project,
        registry: Registry,
    ) -> Storyboard:
        """Create a storyboard from validated project and registry data."""
        ...
