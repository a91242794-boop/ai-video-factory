from dataclasses import dataclass


@dataclass(frozen=True)
class ProjectInfo:
    id: str
    name: str


@dataclass(frozen=True)
class Product:
    name: str
    category: str
    key_features: tuple[str, ...]
    reference_images: tuple[str, ...]


@dataclass(frozen=True)
class Market:
    country: str
    language: str
    platform: str
    audience: str


@dataclass(frozen=True)
class Video:
    duration_seconds: float
    shot_count: int
    aspect_ratio: str


@dataclass(frozen=True)
class Creative:
    hook: str
    tone: str
    environment: str
    character: str
    cta: str


@dataclass(frozen=True)
class Project:
    project: ProjectInfo
    product: Product
    market: Market
    video: Video
    creative: Creative

