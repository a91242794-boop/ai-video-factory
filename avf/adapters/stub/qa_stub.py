"""Local QA adapter with no model dependency."""

from avf.adapters.base import successful_stub_result
from avf.capabilities.requests import CapabilityRequest, QARequest
from avf.capabilities.results import CapabilityResult
from avf.capabilities.types import CapabilityType


class QAStubAdapter:
    provider_id = "stub-qa"
    capability = CapabilityType.QUALITY_ASSURANCE

    def execute(
        self,
        request: CapabilityRequest,
    ) -> CapabilityResult:
        if not isinstance(request, QARequest):
            raise TypeError("QAStubAdapter requires QARequest")
        return successful_stub_result(
            provider_id=self.provider_id,
            capability=self.capability,
            output={
                "stub": True,
                "project_id": request.project_id,
                "target_type": request.target_type,
                "minimum_score": request.minimum_score,
            },
        )
