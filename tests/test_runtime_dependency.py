from dataclasses import FrozenInstanceError

import pytest

from avf.runtime import ModuleDependency


def test_module_dependency_is_immutable_and_normalized() -> None:
    dependency = ModuleDependency(
        module_id="video",
        requires=("director", "image"),
    )

    assert dependency.module_id == "video"
    assert dependency.requires == ("director", "image")
    with pytest.raises(FrozenInstanceError):
        dependency.module_id = "changed"


@pytest.mark.parametrize(
    ("module_id", "requires", "message"),
    [
        (" ", (), "module_id"),
        ("video", (" ",), "dependency"),
        ("video", ("video",), "depend on itself"),
        ("video", ("image", "image"), "unique"),
    ],
)
def test_module_dependency_rejects_invalid_descriptions(
    module_id: str,
    requires: tuple[str, ...],
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        ModuleDependency(module_id=module_id, requires=requires)
