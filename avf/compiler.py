from avf.models import Project
from avf.registry import Registry
from avf.storyboard_models import Storyboard


def compile_gpt_image_prompt(
    project: Project,
    registry: Registry,
    storyboard: Storyboard,
) -> str:
    references = ", ".join(project.product.reference_images)
    lines = [
        f"# {registry.compiler_target} Storyboard Prompt",
        "",
        (
            "Generate a 2x3, 6-panel storyboard read left-to-right, top-to-bottom. "
            f"Every panel must be independently crop-safe for {project.video.aspect_ratio} "
            "vertical video."
        ),
        "",
        "## PRODUCT REFERENCE LOCK",
        (
            f"Use the supplied reference images ({references}) as the only visual source "
            f"of truth for {project.product.name}. Preserve exact packaging, colors, "
            "proportions, label geometry, and scale. Do not redesign the product."
        ),
        "",
        "## CONSISTENCY LOCK",
        f"- Character: {project.creative.character}.",
        f"- Environment: {project.creative.environment}.",
        f"- Tone: {project.creative.tone}.",
        "- Keep the same character identity, wardrobe, environment, lighting, and product.",
        "",
        "## PANELS",
    ]
    for shot in storyboard.shots:
        lines.append(
            f"{shot.id}. [{shot.purpose}] [{shot.shot}] {shot.visual}; "
            f"{shot.action}. Product visibility: {shot.product_visibility}."
        )
    lines.extend(
        [
            "",
            "## LAYOUT",
            (
                "Use thin plain white gutters, clear distinct compositions, and no "
                "repeated panel composition."
            ),
            "",
            "## NEGATIVE CONSTRAINTS",
            (
                "no subtitles, no captions, no title, no panel numbers, no watermark, "
                "no illegible text, no invented logos, no redesigned packaging, no "
                "duplicate panels, no malformed hands, and no unverified claims."
            ),
            "",
        ]
    )
    return "\n".join(lines)
