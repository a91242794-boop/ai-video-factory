import pytest

from avf.capabilities.types import (
    CapabilityType,
    CostTier,
    QualityTier,
    SpeedTier,
)


@pytest.mark.parametrize(
    ("enum_type", "values"),
    [
        (
            CapabilityType,
            (
                "director",
                "image_generation",
                "video_generation",
                "quality_assurance",
            ),
        ),
        (CostTier, ("free", "low", "balanced", "premium")),
        (QualityTier, ("draft", "standard", "high", "premium")),
        (SpeedTier, ("slow", "balanced", "fast")),
    ],
)
def test_capability_enums_use_stable_lowercase_values(
    enum_type: type,
    values: tuple[str, ...],
) -> None:
    assert tuple(item.value for item in enum_type) == values


@pytest.mark.parametrize(
    ("enum_type", "raw", "expected"),
    [
        (CapabilityType, "director", CapabilityType.DIRECTOR),
        (CostTier, "free", CostTier.FREE),
        (QualityTier, "standard", QualityTier.STANDARD),
        (SpeedTier, "fast", SpeedTier.FAST),
    ],
)
def test_capability_enums_parse_valid_strings(
    enum_type: type,
    raw: str,
    expected: object,
) -> None:
    assert enum_type.parse(raw) is expected


@pytest.mark.parametrize(
    "enum_type",
    (CapabilityType, CostTier, QualityTier, SpeedTier),
)
def test_capability_enums_reject_invalid_strings_with_clear_error(
    enum_type: type,
) -> None:
    with pytest.raises(ValueError, match="Unsupported .* value: 'unknown'"):
        enum_type.parse("unknown")
