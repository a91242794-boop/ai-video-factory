import pytest

from avf.intelligence import OptimizationScore, Optimizer, QualityScore


def test_optimizer_calculates_deterministic_quality_cost_score() -> None:
    result = Optimizer().optimize(
        quality_score=80,
        estimated_cost=0.25,
        provider_id="provider-a",
    )

    assert result == OptimizationScore(
        provider_id="provider-a",
        quality_score=QualityScore(80),
        estimated_cost=0.25,
        composite_score=79,
    )


def test_optimizer_rewards_equal_quality_at_lower_cost() -> None:
    optimizer = Optimizer()

    free = optimizer.optimize(
        quality_score=80,
        estimated_cost=0,
        provider_id="free",
    )
    paid = optimizer.optimize(
        quality_score=80,
        estimated_cost=0.5,
        provider_id="paid",
    )

    assert free.composite_score > paid.composite_score


@pytest.mark.parametrize(
    ("provider_id", "estimated_cost", "message"),
    [
        ("", 0, "provider_id"),
        ("provider", -0.1, "estimated_cost"),
    ],
)
def test_optimizer_rejects_invalid_inputs(
    provider_id: str,
    estimated_cost: float,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        Optimizer().optimize(
            quality_score=80,
            estimated_cost=estimated_cost,
            provider_id=provider_id,
        )
