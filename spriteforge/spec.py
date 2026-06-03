from dataclasses import dataclass, field
from typing import Any


@dataclass
class SpriteSpec:
    subject: str = "robot"
    action: str = "run"
    frames: int = 8
    width: int = 32
    height: int = 32
    palette: str = "blue_neon"
    name: str = "robot_run_32x32_8frames"
    category: str = "character"
    features: list[str] = field(default_factory=list)
    raw_prompt: str = ""
    is_fallback: bool = False
    is_unknown: bool = False
    asset_plan: Any = None
    seed: int | None = None
    variant_id: int | None = None
