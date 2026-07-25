from typing import Any

from avf.registry import Registry
from avf.storyboard_models import Storyboard


def run_static_qa(
    storyboard: Storyboard,
    prompt: str,
    registry: Registry,
) -> dict[str, Any]:
    shots = storyboard.shots
    visuals = [shot.visual.strip().casefold() for shot in shots]
    reveal_ids = [shot.id for shot in shots if shot.purpose == "product_reveal"]
    required_fields = (
        "purpose",
        "shot",
        "visual",
        "action",
        "product_visibility",
        "continuity",
    )
    prompt_lower = prompt.casefold()

    checks = {
        "shot_count": len(shots) == 6,
        "sequential_ids": tuple(shot.id for shot in shots) == tuple(range(1, 7)),
        "purpose_sequence": tuple(shot.purpose for shot in shots)
        == registry.qa_required_purposes,
        "product_reveal_by_shot_3": bool(reveal_ids) and min(reveal_ids) <= 3,
        "unique_visuals": len(visuals) == 6 and len(set(visuals)) == len(visuals),
        "required_fields": all(
            shot.duration > 0
            and all(
                isinstance(getattr(shot, field), str)
                and bool(getattr(shot, field).strip())
                for field in required_fields
            )
            for shot in shots
        ),
        "prompt_has_all_shots": all(
            f"{shot.id}. [{shot.purpose}]" in prompt for shot in shots
        )
        and len(shots) == 6,
        "prompt_has_reference_lock": "only visual source of truth" in prompt_lower,
        "prompt_forbids_text": all(
            phrase in prompt_lower
            for phrase in ("no subtitles", "no watermark", "no illegible text")
        ),
    }
    issues = [f"failed_{name}" for name, passed in checks.items() if not passed]
    score = max(0, 100 - 15 * len(issues))
    return {
        "score": score,
        "pass": score >= registry.minimum_qa_score and not issues,
        "issues": issues,
        "checks": checks,
        "model_tokens_used": 0,
    }
