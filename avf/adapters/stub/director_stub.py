"""Local Director adapter with no model dependency."""

from avf.adapters.base import successful_stub_result
from avf.capabilities.requests import (
    CapabilityRequest,
    DirectorRequest,
)
from avf.capabilities.results import CapabilityResult
from avf.capabilities.types import CapabilityType


class DirectorStubAdapter:
    provider_id = "stub-director"
    capability = CapabilityType.DIRECTOR

    def execute(
        self,
        request: CapabilityRequest,
    ) -> CapabilityResult:
        if not isinstance(request, DirectorRequest):
            raise TypeError("DirectorStubAdapter requires DirectorRequest")
        return successful_stub_result(
            provider_id=self.provider_id,
            capability=self.capability,
            output={
                "stub": True,
                "project_id": request.project_id,
                "shot_count": request.shot_count,
            },
        )
