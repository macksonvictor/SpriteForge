from dataclasses import dataclass, field

from .spec import SpriteSpec


ACCESSORY_FEATURES = {
    "sword": "sword",
    "shield": "shield",
    "staff": "staff",
    "bow": "bow",
    "knife": "knife",
    "armor": "armor_plate",
    "wings": "wings",
    "horns": "horns",
    "tail": "tail",
}

ELEMENT_FEATURES = {
    "fire": "fire",
    "ice": "ice",
    "stone": "stone",
    "magic": "magic",
    "smoke": "smoke",
}


@dataclass
class AssetPlan:
    subject: str
    category: str
    asset_family: str
    body_type: str
    base_template: str
    action: str
    palette: list[str] = field(default_factory=list)
    features: list[str] = field(default_factory=list)
    accessories: list[str] = field(default_factory=list)
    element: str = "none"
    animation_style: str = "idle_bob"
    size: tuple[int, int] = (32, 32)
    frames: int = 1


def build_asset_plan(spec: SpriteSpec) -> AssetPlan:
    body_type = _body_type(spec)
    base_template = _base_template(spec, body_type)
    accessories = _accessories(spec)
    element = _element(spec)
    features = _semantic_features(spec, accessories, element)

    return AssetPlan(
        subject=spec.subject,
        category=spec.category,
        asset_family=_asset_family(spec),
        body_type=body_type,
        base_template=base_template,
        action=spec.action,
        palette=_semantic_palette(spec, features, accessories, element),
        features=features,
        accessories=accessories,
        element=element,
        animation_style=_animation_style(spec.action),
        size=(spec.width, spec.height),
        frames=spec.frames,
    )


def _body_type(spec: SpriteSpec) -> str:
    if spec.subject == "sapo":
        return "frog"
    if spec.subject in ["capivara", "cachorro", "gato", "lobo"]:
        return "quadruped"
    if spec.subject == "urso":
        return "bear"
    if spec.subject in ["dragao", "passaro", "morcego"]:
        return "winged"
    if spec.subject in ["monstro", "goblin", "zumbi", "alien"]:
        if "stone" in spec.features or spec.palette == "stone":
            return "stone_monster"
        return "monster"
    if spec.subject == "slime":
        return "blob"
    if spec.category == "item":
        return "item"
    if spec.category == "effect":
        return "effect"
    if spec.category == "background":
        return "background"
    return "humanoid"


def _base_template(spec: SpriteSpec, body_type: str) -> str:
    if spec.category in ["creature", "character"]:
        if body_type == "stone_monster":
            return "monster"
        return body_type

    if spec.category == "item":
        item_templates = {
            "sword": "sword",
            "shield": "shield",
            "potion": "potion",
            "coin": "coin",
            "key": "key",
            "knife": "knife",
            "bow": "bow",
            "staff": "staff",
        }
        return item_templates.get(spec.subject, "item")

    if spec.category == "effect":
        effect_templates = {
            "portal": "portal",
            "explosion": "explosion",
            "fire": "flame",
            "ice": "glow",
            "glow": "glow",
            "magic": "glow",
            "aura": "glow",
            "energy": "glow",
            "smoke": "smoke",
            "star": "glow",
        }
        return effect_templates.get(spec.subject, "glow")

    if spec.category == "background":
        background_templates = {
            "floresta": "forest",
            "arvore": "tree",
            "nuvem": "cloud",
            "montanha": "mountain",
            "chao": "platformer_ground",
            "pedra": "platformer_ground",
            "plataforma": "platformer_ground",
            "grama": "platformer_ground",
        }
        return background_templates.get(spec.subject, "forest")

    return "unknown"


def _asset_family(spec: SpriteSpec) -> str:
    if spec.category == "character":
        return "creature"
    if spec.category in ["creature", "item", "effect", "background"]:
        return spec.category
    return "unknown"


def _accessories(spec: SpriteSpec) -> list[str]:
    accessories = []

    for feature in spec.features:
        if spec.category == "item" and feature == spec.subject:
            continue
        accessory = ACCESSORY_FEATURES.get(feature)
        if accessory and accessory not in accessories:
            accessories.append(accessory)

    if spec.subject in ["dragao", "passaro", "morcego"] and "wings" not in accessories:
        accessories.append("wings")
    if spec.subject == "dragao" and "horns" not in accessories:
        accessories.append("horns")
    if spec.subject == "dragao" and "tail" not in accessories:
        accessories.append("tail")

    return accessories


def _element(spec: SpriteSpec) -> str:
    if spec.subject == "explosion":
        return "fire"
    if spec.subject in ["fire", "ice", "smoke", "magic"]:
        return {"fire": "fire", "ice": "ice", "smoke": "smoke", "magic": "magic"}[spec.subject]

    for feature in spec.features:
        element = ELEMENT_FEATURES.get(feature)
        if element:
            return element

    return "none"


def _semantic_features(spec: SpriteSpec, accessories: list[str], element: str) -> list[str]:
    accessory_source = set(ACCESSORY_FEATURES)
    element_source = set(ELEMENT_FEATURES)
    features = []

    for feature in spec.features:
        if feature in accessory_source or feature in element_source:
            continue
        if feature not in features:
            features.append(feature)

    if "ninja" in spec.features and "ninja" not in features:
        features.append("ninja")
    if "warrior" in spec.features and "warrior" not in features:
        features.append("warrior")
    if "red_eyes" in spec.features and "red_eyes" not in features:
        features.append("red_eyes")

    return features


def _semantic_palette(
    spec: SpriteSpec,
    features: list[str],
    accessories: list[str],
    element: str,
) -> list[str]:
    colors = []

    subject_colors = {
        "sapo": ["green"],
        "capivara": ["brown"],
        "urso": ["brown"],
        "cachorro": ["brown"],
        "gato": ["gray"],
        "monstro": ["gray"] if element == "stone" else ["green"],
        "dragao": ["green"],
        "alien": ["green"],
        "zumbi": ["green"],
        "goblin": ["green"],
        "coin": ["gold"],
        "potion": ["purple"],
        "portal": ["purple"],
        "floresta": ["green", "dark"],
    }

    colors.extend(subject_colors.get(spec.subject, []))

    palette_colors = {
        "blue_neon": ["blue", "cyan"],
        "green_neon": ["green"],
        "purple_neon": ["purple"],
        "red_neon": ["red"],
        "fire": ["orange", "red", "yellow"],
        "stone": ["gray"],
    }
    colors.extend(palette_colors.get(spec.palette, []))

    if "ninja" in features:
        colors.append("black")
    if "armor_plate" in accessories:
        colors.append("silver")
    if element == "fire":
        colors.extend(["orange", "red"])
    elif element == "ice":
        colors.extend(["blue", "white"])
    elif element == "magic":
        colors.append("purple")
    elif element == "smoke":
        colors.append("gray")

    deduped = []
    for color in colors:
        if color not in deduped:
            deduped.append(color)

    return deduped or ["blue"]


def _animation_style(action: str) -> str:
    styles = {
        "idle": "idle_bob",
        "walk": "walk_cycle",
        "run": "run_cycle",
        "jump": "jump_arc",
        "fly": "fly_flap",
        "attack": "attack_swing",
        "glow": "glow_pulse",
        "blink": "blink",
        "spin": "spin",
        "explode": "explosion",
    }
    return styles.get(action, "idle_bob")
