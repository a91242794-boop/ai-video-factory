from avf.models import Project
from avf.storyboard_models import Shot, Storyboard


def generate_storyboard(project: Project) -> Storyboard:
    duration = project.video.duration_seconds / project.video.shot_count
    shared = (
        f"same {project.creative.character}; same {project.creative.environment}; "
        f"{project.creative.tone}"
    )
    product = project.product.name
    feature = project.product.key_features[0]
    shots = (
        Shot(1, "hook", duration, "CU", project.creative.hook,
             "The creator notices the problem during the opening moment",
             "none", shared),
        Shot(2, "problem", duration, "MACRO",
             f"A clear close-up of the everyday {project.product.category} concern",
             "The creator examines the problem naturally", "none", shared),
        Shot(3, "product_reveal", duration, "HERO",
             f"{product} enters frame with packaging facing camera",
             "The creator reaches for the product", "hero", shared),
        Shot(4, "use", duration, "CU", f"Natural application of {product}",
             "The creator demonstrates simple daily use", "in_use", shared),
        Shot(5, "benefit", duration, "MCU",
             f"A clean, credible visual expressing {feature}",
             "The creator completes the routine with a reassured expression",
             "visible", shared),
        Shot(6, "cta_plate", duration, "HERO",
             f"{product} on a clean background with empty layout space",
             project.creative.cta, "hero", shared),
    )
    return Storyboard(
        project_id=project.project.id,
        format=project.video.aspect_ratio,
        layout="2x3",
        shots=shots,
    )
