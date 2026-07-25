import pytest

from avf.capabilities.requests import (
    CapabilityRequest,
    DirectorRequest,
    ImageGenerationRequest,
    QARequest,
    VideoGenerationRequest,
)
from avf.capabilities.types import (
    CapabilityType,
    CostTier,
    QualityTier,
    SpeedTier,
)


def test_base_request_preserves_provider_priority_and_serializes_stably() -> None:
    request = CapabilityRequest(
        capability=CapabilityType.IMAGE_GENERATION,
        project_id="mini",
        cost_tier=CostTier.FREE,
        quality_tier=QualityTier.STANDARD,
        speed_tier=SpeedTier.BALANCED,
        max_cost=1.5,
        preferred_providers=("first", "second"),
        metadata={"z": 2, "a": 1},
    )

    assert request.preferred_providers == ("first", "second")
    assert request.to_dict() == request.to_dict()
    assert request.to_dict() == {
        "capability": "image_generation",
        "project_id": "mini",
        "cost_tier": "free",
        "quality_tier": "standard",
        "speed_tier": "balanced",
        "max_cost": 1.5,
        "preferred_providers": ["first", "second"],
        "excluded_providers": [],
        "metadata": {"a": 1, "z": 2},
    }


def test_request_metadata_has_no_shared_mutable_default() -> None:
    first = CapabilityRequest(
        capability=CapabilityType.DIRECTOR,
        project_id="first",
    )
    second = CapabilityRequest(
        capability=CapabilityType.DIRECTOR,
        project_id="second",
    )

    first.metadata["source"] = "test"

    assert second.metadata == {}


@pytest.mark.parametrize("max_cost", (-0.01, -1))
def test_request_rejects_negative_max_cost(max_cost: float) -> None:
    with pytest.raises(ValueError, match="max_cost must be zero or greater"):
        CapabilityRequest(
            capability=CapabilityType.DIRECTOR,
            project_id="mini",
            max_cost=max_cost,
        )


def test_request_rejects_overlapping_provider_preferences() -> None:
    with pytest.raises(
        ValueError,
        match="preferred_providers and excluded_providers overlap: shared",
    ):
        CapabilityRequest(
            capability=CapabilityType.DIRECTOR,
            project_id="mini",
            preferred_providers=("shared", "preferred"),
            excluded_providers=("shared",),
        )


def test_director_request_requires_a_project_source() -> None:
    with pytest.raises(
        ValueError,
        match="DirectorRequest requires project_path or project_data",
    ):
        DirectorRequest(project_id="mini")


def test_specific_requests_set_capability_and_serialize_payloads() -> None:
    director = DirectorRequest(
        project_id="mini",
        project_path="examples/mini/project.yaml",
        shot_count=6,
    )
    image = ImageGenerationRequest(
        project_id="mini",
        storyboard={"shots": [1, 2]},
        reference_images=("front.png",),
        output_format="png",
    )
    video = VideoGenerationRequest(
        project_id="mini",
        storyboard={"shots": [1, 2]},
        image_assets=("shot-1.png",),
        duration_seconds=15,
    )
    qa = QARequest(
        project_id="mini",
        target_type="storyboard",
        payload={"shots": 6},
        minimum_score=85,
    )

    assert director.capability is CapabilityType.DIRECTOR
    assert image.capability is CapabilityType.IMAGE_GENERATION
    assert video.capability is CapabilityType.VIDEO_GENERATION
    assert qa.capability is CapabilityType.QUALITY_ASSURANCE
    assert image.to_dict()["reference_images"] == ["front.png"]
    assert video.to_dict()["duration_seconds"] == 15


@pytest.mark.parametrize(
    ("factory", "message"),
    [
        (
            lambda: DirectorRequest(
                project_id="mini",
                project_path="project.yaml",
                shot_count=0,
            ),
            "shot_count must be greater than zero",
        ),
        (
            lambda: VideoGenerationRequest(
                project_id="mini",
                storyboard={},
                duration_seconds=-1,
            ),
            "duration_seconds must be zero or greater",
        ),
        (
            lambda: QARequest(
                project_id="mini",
                target_type="prompt",
                payload={},
                minimum_score=101,
            ),
            "minimum_score must be between 0 and 100",
        ),
    ],
)
def test_specific_requests_reject_invalid_limits(factory, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        factory()
