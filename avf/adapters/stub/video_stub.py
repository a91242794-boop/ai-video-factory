"""Local Video adapter with no model dependency."""

from avf.adapters.base import successful_stub_result
from avf.capabilities.requests import (
    CapabilityRequest,
    VideoGenerationRequest,
)
from avf.capabilities.results import CapabilityResult
from avf.capabilities.types import CapabilityType


class VideoStubAdapter:
    provider_id = "stub-video"
    capability = CapabilityType.VIDEO_GENERATION

    def execute(
        self,
        request: CapabilityRequest,
    ) -> CapabilityResult:
        if not isinstance(request, VideoGenerationRequest):
            raise TypeError(
                "VideoStubAdapter requires VideoGenerationRequest"
            )
        return successful_stub_result(
            provider_id=self.provider_id,
            capability=self.capability,
            output={
                "stub": True,
                "project_id": request.project_id,
                "duration_seconds": request.duration_seconds,
            },
        )
