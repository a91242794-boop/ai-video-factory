"""Contract for image generation providers."""

from typing import Protocol, Sequence, TypeVar

ImageResultT_co = TypeVar("ImageResultT_co", covariant=True)


class ImageProviderContract(Protocol[ImageResultT_co]):
    """Generate an image artifact without prescribing a provider SDK."""

    def generate_image(
        self,
        prompt: str,
        reference_images: Sequence[str],
    ) -> ImageResultT_co:
        """Generate an image artifact from a prompt and optional references."""
        ...
