"""Provider fallback policy based on Router candidate ordering."""

from avf.capabilities.registry import ProviderDescriptor
from avf.capabilities.requests import CapabilityRequest
from avf.router.router import ProviderRouter


class FallbackPolicy:
    def __init__(self, router: ProviderRouter) -> None:
        self._router = router

    def candidates(
        self,
        request: CapabilityRequest,
    ) -> list[ProviderDescriptor]:
        return self._router.select_candidates(request)
