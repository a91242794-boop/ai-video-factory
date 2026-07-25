from dataclasses import dataclass


@dataclass(frozen=True)
class Shot:
    id: int
    purpose: str
    duration: float
    shot: str
    visual: str
    action: str
    product_visibility: str
    continuity: str


@dataclass(frozen=True)
class Storyboard:
    project_id: str
    format: str
    layout: str
    shots: tuple[Shot, ...]
