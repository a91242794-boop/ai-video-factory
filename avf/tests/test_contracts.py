from inspect import signature

from avf.contracts import (
    DirectorContract,
    ImageProviderContract,
    QAContract,
    VideoProviderContract,
)


def test_module_contracts_are_protocols() -> None:
    contracts = (
        DirectorContract,
        ImageProviderContract,
        VideoProviderContract,
        QAContract,
    )

    assert all(getattr(contract, "_is_protocol", False) for contract in contracts)


def test_director_contract_exposes_storyboard_generation() -> None:
    parameters = signature(DirectorContract.create_storyboard).parameters

    assert tuple(parameters) == ("self", "project", "registry")


def test_image_provider_contract_exposes_provider_neutral_generation() -> None:
    parameters = signature(ImageProviderContract.generate_image).parameters

    assert tuple(parameters) == ("self", "prompt", "reference_images")


def test_video_provider_contract_exposes_provider_neutral_generation() -> None:
    parameters = signature(VideoProviderContract.generate_video).parameters

    assert tuple(parameters) == ("self", "storyboard", "image_assets")


def test_qa_contract_exposes_static_qa_inputs() -> None:
    parameters = signature(QAContract.evaluate).parameters

    assert tuple(parameters) == ("self", "storyboard", "prompt", "registry")
