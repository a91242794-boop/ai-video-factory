"""Local Image adapter with no model dependency."""

from avf.adapters.base import successful_stub_result
from avf.capabilities.requests import (
    CapabilityRequest,
    ImageGenerationRequest,
)
from avf.capabilities.results import CapabilityResult
from avf.capabilities.types import CapabilityType


class ImageStubAdapter:
    provider_id = "stub-image"
    capability = CapabilityType.IMAGE_GENERATION

    def execute(
        self,
        request: CapabilityRequest,
    ) -> CapabilityResult:
        if not isinstance(request, ImageGenerationRequest):
            raise TypeError(
                "ImageStubAdapter requires ImageGenerationRequest"
            )
        return successful_stub_result(
            provider_id=self.provider_id,
            capability=self.capability,
            output={
                "stub": True,
                "project_id": request.project_id,
                "output_format": request.output_format,
            },
        )
