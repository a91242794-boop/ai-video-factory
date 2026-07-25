from dataclasses import FrozenInstanceError

import pytest

from avf.runtime import ModuleMetadata


def test_module_metadata_is_immutable_and_zero_cost() -> None:
    metadata = ModuleMetadata(
        module_id="storyboard",
        name="Storyboard Module",
        version="1.0.0",
    )

    assert metadata.module_id == "storyboard"
    assert metadata.name == "Storyboard Module"
    assert metadata.version == "1.0.0"
    assert metadata.cost == 0
    with pytest.raises(FrozenInstanceError):
        metadata.name = "Changed"


@pytest.mark.parametrize(
    ("values", "message"),
    [
        (
            {"module_id": " ", "name": "Example", "version": "1.0.0"},
            "module_id",
        ),
        (
            {"module_id": "example", "name": " ", "version": "1.0.0"},
            "name",
        ),
        (
            {"module_id": "example", "name": "Example", "version": " "},
            "version",
        ),
    ],
)
def test_module_metadata_rejects_blank_required_fields(
    values: dict[str, str],
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        ModuleMetadata(**values)


def test_module_metadata_rejects_nonzero_cost() -> None:
    with pytest.raises(ValueError, match="cost must remain zero"):
        ModuleMetadata(
            module_id="paid",
            name="Paid Module",
            version="1.0.0",
            cost=0.01,
        )
