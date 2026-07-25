"""Contract for video generation providers."""

from typing import Protocol, Sequence, TypeVar

from avf.storyboard_models import Storyboard

VideoResultT_co = TypeVar("VideoResultT_co", covariant=True)


class VideoProviderContract(Protocol[VideoResultT_co]):
    """Generate a video artifact without prescribing a provider SDK."""

    def generate_video(
        self,
        storyboard: Storyboard,
        image_assets: Sequence[object],
    ) -> VideoResultT_co:
        """Generate a video artifact from a storyboard and image assets."""
        ...
