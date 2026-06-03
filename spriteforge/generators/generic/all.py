import math

from ...draw import PixelCanvas
from ...palettes import PALETTES


BLACK = (5, 6, 8, 255)
WHITE = (242, 248, 238, 255)
FIRE_OUTLINE = (80, 18, 6, 255)
FIRE_MID = (240, 80, 10, 255)
FIRE_LIGHT = (255, 210, 50, 255)
GOLD = (238, 178, 42, 255)
SILVER = (178, 188, 196, 255)
BROWN = (126, 92, 66, 255)
DARK_BROWN = (58, 39, 28, 255)
PURPLE = (132, 70, 190, 255)
GLASS = (170, 235, 255, 210)
SMOKE = (90, 94, 100, 180)


def _variation(spec, modulo, salt=0):
    seed = getattr(spec, "seed", 0) or 0
    variant_id = getattr(spec, "variant_id", 0) or 0
    return (seed + variant_id * 97 + salt * 193) % max(1, modulo)


def _variant_shift(spec, salt=0):
    return int(_variation(spec, 3, salt)) - 1


def _plan(spec):
    return getattr(spec, "asset_plan", None)


def _template(spec):
    plan = _plan(spec)
    if plan:
        return plan.base_template
    return getattr(spec, "subject", "unknown")


def _body_type(spec):
    plan = _plan(spec)
    if plan:
        return plan.body_type
    return "humanoid"


def _features(spec):
    plan = _plan(spec)
    if plan:
        return plan.features
    return spec.features


def _accessories(spec):
    plan = _plan(spec)
    if plan:
        return plan.accessories

    fallback = []
    mapping = {
        "ninja": "ninja_band",
        "sword": "sword",
        "armor": "armor_plate",
        "wings": "wings",
        "horns": "horns",
        "tail": "tail",
        "shield": "shield",
        "staff": "staff",
        "bow": "bow",
        "knife": "knife",
    }
    for feature in spec.features:
        accessory = mapping.get(feature)
        if accessory and accessory not in fallback:
            fallback.append(accessory)
    return fallback


def _element(spec):
    plan = _plan(spec)
    if plan:
        return plan.element
    for feature in ["fire", "ice", "stone", "magic", "smoke"]:
        if feature in spec.features:
            return feature
    return "none"


def _palette(spec):
    if spec.subject == "sapo":
        return {
            "outline": (5, 28, 12, 255),
            "dark": (26, 98, 38, 255),
            "mid": (64, 176, 78, 255),
            "light": (152, 232, 110, 255),
            "neon": (74, 255, 125, 255),
            "eye": (12, 18, 14, 255),
            "shadow": (0, 0, 0, 90),
            "white": WHITE,
        }
    if spec.subject in ["capivara", "urso", "cachorro"]:
        return {
            "outline": DARK_BROWN,
            "dark": (82, 57, 42, 255),
            "mid": BROWN,
            "light": (178, 136, 92, 255),
            "neon": SILVER,
            "eye": (12, 10, 8, 255),
            "shadow": (0, 0, 0, 90),
            "white": (230, 220, 200, 255),
        }
    if spec.subject == "dragao":
        return {
            "outline": (8, 22, 18, 255),
            "dark": (24, 74, 52, 255),
            "mid": (58, 148, 86, 255),
            "light": (134, 218, 118, 255),
            "neon": (250, 210, 80, 255),
            "eye": (255, 220, 60, 255),
            "shadow": (0, 0, 0, 90),
            "white": WHITE,
        }
    if spec.subject in ["gato", "monstro", "goblin", "zumbi", "alien"] and _element(spec) != "stone":
        return PALETTES["green_neon"]
    if _element(spec) == "stone":
        return PALETTES["stone"]
    return PALETTES.get(spec.palette, PALETTES["blue_neon"])


def _draw_flame(c, x, y, phase):
    flicker = int(round(math.sin(phase * 2) * 1))
    c.polygon([(x + 2, y - 5 + flicker), (x + 6, y + 1), (x + 3, y + 6), (x, y + 2)], FIRE_OUTLINE)
    c.polygon([(x + 3, y - 3 + flicker), (x + 5, y + 2), (x + 3, y + 5), (x + 1, y + 2)], FIRE_MID)
    c.polygon([(x + 3, y), (x + 4, y + 2), (x + 3, y + 4), (x + 2, y + 2)], FIRE_LIGHT)


def _draw_magic_spark(c, x, y, phase):
    blink = int((math.sin(phase * 2) + 1) * 1.5)
    c.rect(x, y, 2, 2, PURPLE)
    c.rect(x + 3, y - blink, 1, 1, (235, 200, 255, 255))
    c.rect(x - 2, y + 3, 1, 1, (235, 200, 255, 255))


def _draw_tiny_sword(c, x, y, phase, with_fire=False):
    c.line([(x, y), (x + 7, y - 8)], (18, 20, 24, 255), width=2)
    c.line([(x + 1, y - 1), (x + 7, y - 8)], (220, 235, 245, 255), width=1)
    c.line([(x - 1, y + 1), (x + 2, y - 2)], (18, 20, 24, 255), width=2)
    c.rect(x - 2, y + 1, 3, 3, (70, 45, 30, 255))
    if with_fire:
        _draw_flame(c, x + 5, y - 8, phase)


def _draw_tiny_knife(c, x, y):
    c.line([(x, y), (x + 4, y - 5)], (18, 20, 24, 255), width=2)
    c.line([(x + 1, y - 1), (x + 4, y - 5)], (225, 235, 240, 255), width=1)
    c.rect(x - 1, y, 2, 3, (80, 48, 28, 255))


def _draw_shield(c, x, y):
    c.polygon([(x + 4, y), (x + 9, y + 2), (x + 8, y + 9), (x + 4, y + 12), (x, y + 9), (x - 1, y + 2)], BLACK)
    c.polygon([(x + 4, y + 1), (x + 8, y + 3), (x + 7, y + 8), (x + 4, y + 10), (x + 1, y + 8), (x, y + 3)], SILVER)
    c.rect(x + 3, y + 3, 2, 6, (100, 110, 118, 255))


def _draw_armor(c, x, y, w, h):
    c.rect(x, y, w, h, BLACK)
    c.rect(x + 1, y + 1, max(1, w - 2), max(1, h - 2), SILVER)
    c.rect(x + 2, y + 2, max(1, w - 4), 1, (230, 235, 238, 255))
    c.rect(x + w // 2, y + 1, 1, max(1, h - 2), (100, 106, 112, 255))


def _draw_accessory_layers(c, spec, phase, bob):
    accessories = _accessories(spec)
    element = _element(spec)
    dx = _variant_shift(spec, 5)
    dy = _variant_shift(spec, 7)

    if "sword" in accessories:
        _draw_tiny_sword(c, 24 + dx, 20 + bob + dy, phase, element == "fire")
    if "knife" in accessories:
        _draw_tiny_knife(c, 24 + dx, 20 + bob + dy)
    if "shield" in accessories:
        _draw_shield(c, 3 + dx, 15 + bob)
    if "staff" in accessories:
        c.line([(25 + dx, 23 + bob), (29 + dx, 10 + bob)], DARK_BROWN, width=2)
        _draw_magic_spark(c, 27 + dx, 8 + bob, phase)
    if "bow" in accessories:
        c.line([(4, 13 + bob), (3, 22 + bob)], DARK_BROWN, width=2)
        c.line([(4, 13 + bob), (7, 18 + bob), (3, 22 + bob)], (230, 220, 170, 255), width=1)
    if element == "fire" and "sword" not in accessories:
        _draw_flame(c, 25 + dx, 18 + bob, phase)
    elif element == "magic":
        _draw_magic_spark(c, 25, 15 + bob, phase)


def _draw_frog_template(c, spec, phase, bob, step):
    p = _palette(spec)
    accessories = _accessories(spec)
    variant_id = getattr(spec, "variant_id", 0) or 0
    eye_size = 2 + (variant_id % 2 if variant_id else _variation(spec, 2, 11))
    belly_shift = _variant_shift(spec, 13)
    head_w = 20 + _variant_shift(spec, 17)

    c.ellipse(7, 29, 18 + _variant_shift(spec, 19), 2, p["shadow"])
    c.ellipse(5, 22 + bob - step, 8, 5, p["outline"])
    c.ellipse(19, 22 + bob + step, 8, 5, p["outline"])
    c.ellipse(6, 23 + bob - step, 6, 3, p["dark"])
    c.ellipse(20, 23 + bob + step, 6, 3, p["dark"])

    c.ellipse(8, 15 + bob, 16, 12, p["outline"])
    c.ellipse(9, 16 + bob, 14, 10, p["mid"])
    c.ellipse(12, 19 + bob, 8, 5, p["light"])
    c.ellipse(6, 7 + bob, head_w, 12, p["outline"])
    c.ellipse(7, 8 + bob, head_w - 2, 10, p["mid"])
    c.rect(10, 9 + bob, 12, 2, p["light"])

    if "ninja_band" in accessories:
        c.rect(7, 11 + bob, 18, 3, BLACK)
        c.rect(22, 10 + bob, 5, 1, BLACK)
        c.rect(23, 13 + bob, 4, 1, BLACK)

    c.ellipse(8, 4 + bob, 6, 6, p["outline"])
    c.ellipse(18, 4 + bob, 6, 6, p["outline"])
    c.ellipse(9, 5 + bob, 4, 4, WHITE)
    c.ellipse(19, 5 + bob, 4, 4, WHITE)
    c.rect(11, 7 + bob, eye_size, eye_size, p["eye"])
    c.rect(20, 7 + bob, eye_size, eye_size, p["eye"])
    c.rect(12, 15 + bob, 8, 1, p["outline"])
    c.rect(10, 24 + bob, 4, 3, p["outline"])
    c.rect(19, 24 + bob, 4, 3, p["outline"])
    c.rect(12 + belly_shift, 20 + bob, 4, 1, p["light"])
    if variant_id:
        c.rect(8, 16 + bob, 2, 1, p["dark"])
        c.rect(22, 16 + bob, 2, 1, p["dark"])
        c.rect(14 + (variant_id % 3), 21 + bob, 3, 1, p["neon"])

    _draw_accessory_layers(c, spec, phase, bob)


def _draw_quadruped_template(c, spec, phase, bob, step):
    p = _palette(spec)
    accessories = _accessories(spec)

    c.ellipse(6, 29, 21, 2, p["shadow"])
    c.ellipse(6, 16 + bob, 19, 10, p["outline"])
    c.ellipse(7, 17 + bob, 17, 8, p["mid"])
    c.rect(10, 17 + bob, 8, 2, p["light"])

    if "armor_plate" in accessories:
        _draw_armor(c, 10, 16 + bob, 11, 8)

    c.ellipse(20, 12 + bob, 8, 8, p["outline"])
    c.ellipse(21, 13 + bob, 6, 6, p["mid"])
    c.rect(24, 16 + bob, 5, 4, p["outline"])
    c.rect(24, 16 + bob, 4, 3, p["light"])
    c.rect(21, 10 + bob, 3, 3, p["outline"])
    c.rect(22, 11 + bob, 1, 1, p["light"])
    c.rect(24, 14 + bob, 1, 1, p["eye"])
    c.rect(28, 18 + bob, 1, 1, p["eye"])

    c.rect(9 + step, 24 + bob, 3, 5, p["outline"])
    c.rect(15 - step, 24 + bob, 3, 5, p["outline"])
    c.rect(22 + step, 23 + bob, 3, 5, p["outline"])
    c.rect(9 + step, 27 + bob, 5, 2, p["dark"])
    c.rect(15 - step, 27 + bob, 5, 2, p["dark"])
    c.rect(22 + step, 26 + bob, 5, 2, p["dark"])

    if "tail" in accessories or spec.subject in ["gato", "cachorro", "lobo"]:
        c.line([(7, 20 + bob), (3, 17 + bob), (2, 14 + bob)], p["outline"], width=2)


def _draw_bear_template(c, spec, phase, bob, step):
    p = _palette(spec)

    c.ellipse(6, 29, 21, 2, p["shadow"])
    c.ellipse(7, 13 + bob, 18, 15, p["outline"])
    c.ellipse(8, 14 + bob, 16, 13, p["mid"])
    c.ellipse(9, 7 + bob, 14, 12, p["outline"])
    c.ellipse(10, 8 + bob, 12, 10, p["mid"])
    c.ellipse(8, 6 + bob, 5, 5, p["outline"])
    c.ellipse(19, 6 + bob, 5, 5, p["outline"])
    c.ellipse(12, 13 + bob, 8, 5, p["light"])
    c.rect(12, 11 + bob, 2, 2, p["eye"])
    c.rect(19, 11 + bob, 2, 2, p["eye"])
    c.rect(15, 14 + bob, 2, 1, p["outline"])
    c.rect(8, 19 + bob + step, 4, 7, p["outline"])
    c.rect(22, 19 + bob - step, 4, 7, p["outline"])
    c.rect(10 + step, 25 + bob, 5, 4, p["outline"])
    c.rect(18 - step, 25 + bob, 5, 4, p["outline"])

    if "warrior" in _features(spec):
        c.rect(11, 18 + bob, 10, 6, BLACK)
        c.rect(12, 19 + bob, 8, 4, (120, 95, 70, 255))

    _draw_accessory_layers(c, spec, phase, bob)


def _draw_monster_template(c, spec, phase, bob, step):
    p = _palette(spec)
    stone = _element(spec) == "stone"
    accessories = _accessories(spec)

    c.ellipse(7, 29, 18, 2, p["shadow"])
    if stone:
        c.polygon([(10, 8 + bob), (20, 7 + bob), (25, 13 + bob), (24, 24 + bob), (18, 28 + bob), (9, 25 + bob), (6, 15 + bob)], p["outline"])
        c.polygon([(11, 10 + bob), (19, 9 + bob), (23, 14 + bob), (22, 23 + bob), (17, 26 + bob), (10, 23 + bob), (8, 15 + bob)], p["mid"])
        c.rect(12, 12 + bob, 4, 3, p["dark"])
        c.rect(18, 15 + bob, 4, 4, p["light"])
        c.line([(15, 15 + bob), (13, 19 + bob), (16, 22 + bob)], p["outline"], width=1)
        c.line([(20, 11 + bob), (18, 13 + bob)], p["outline"], width=1)
    else:
        c.ellipse(8, 12 + bob, 16, 15, p["outline"])
        c.ellipse(9, 13 + bob, 14, 13, p["mid"])
        c.rect(6, 17 + bob + step, 5, 5, p["outline"])
        c.rect(22, 17 + bob - step, 5, 5, p["outline"])

    eye = (255, 35, 55, 255) if "red_eyes" in _features(spec) or stone else p["eye"]
    c.rect(12, 14 + bob, 3, 2, eye)
    c.rect(19, 14 + bob, 3, 2, eye)
    c.rect(14, 20 + bob, 6, 1, p["outline"])
    c.rect(10 + step, 26 + bob, 5, 3, p["outline"])
    c.rect(18 - step, 26 + bob, 5, 3, p["outline"])

    if "horns" in accessories:
        c.polygon([(12, 10 + bob), (9, 4 + bob), (15, 9 + bob)], p["outline"])
        c.polygon([(20, 10 + bob), (23, 4 + bob), (17, 9 + bob)], p["outline"])
    if "armor_plate" in accessories:
        _draw_armor(c, 11, 18 + bob, 10, 5)

    _draw_accessory_layers(c, spec, phase, bob)


def _draw_winged_template(c, spec, phase, bob, step):
    p = _palette(spec)
    accessories = _accessories(spec)

    c.ellipse(7, 29, 18, 2, p["shadow"])
    c.polygon([(10, 15 + bob), (3, 7 + bob - step), (8, 21 + bob)], p["outline"])
    c.polygon([(18, 14 + bob), (28, 6 + bob + step), (23, 21 + bob)], p["outline"])
    c.polygon([(10, 15 + bob), (4, 9 + bob - step), (8, 19 + bob)], p["mid"])
    c.polygon([(18, 14 + bob), (27, 8 + bob + step), (23, 19 + bob)], p["mid"])
    c.ellipse(8, 16 + bob, 16, 9, p["outline"])
    c.ellipse(9, 17 + bob, 14, 7, p["mid"])
    c.rect(20, 13 + bob, 3, 5, p["outline"])
    c.ellipse(21, 9 + bob, 8, 7, p["outline"])
    c.ellipse(22, 10 + bob, 6, 5, p["mid"])
    c.rect(27, 12 + bob, 3, 3, p["outline"])
    c.rect(25, 11 + bob, 1, 1, p["eye"])
    c.polygon([(9, 21 + bob), (4, 20 + bob), (1, 17 + bob), (6, 18 + bob)], p["outline"])

    if "horns" in accessories:
        c.polygon([(23, 10 + bob), (22, 6 + bob), (25, 10 + bob)], p["neon"])
        c.polygon([(27, 11 + bob), (29, 8 + bob), (28, 12 + bob)], p["neon"])
    if _element(spec) == "fire":
        _draw_flame(c, 29, 13 + bob, phase)


def _draw_humanoid_template(c, spec, phase, bob, step):
    p = _palette(spec)
    c.ellipse(7, 29, 18, 2, p["shadow"])
    c.ellipse(9, 15 + bob, 14, 12, p["outline"])
    c.ellipse(10, 16 + bob, 12, 10, p["mid"])
    c.ellipse(10, 7 + bob, 12, 10, p["outline"])
    c.ellipse(11, 8 + bob, 10, 8, p["light"])
    c.rect(13, 11 + bob, 2, 2, p["eye"])
    c.rect(18, 11 + bob, 2, 2, p["eye"])
    c.rect(11 + step, 25 + bob, 4, 4, p["outline"])
    c.rect(18 - step, 25 + bob, 4, 4, p["outline"])
    _draw_accessory_layers(c, spec, phase, bob)


def generate_generic_creature(spec):
    frames = []

    for i in range(spec.frames):
        phase = (i / max(1, spec.frames)) * math.tau
        bob = int(round(math.sin(phase) * 1))
        step = int(round(math.sin(phase) * 2))
        c = PixelCanvas(spec.width, spec.height, 32, 32)
        template = _template(spec)
        body_type = _body_type(spec)

        if template == "frog":
            _draw_frog_template(c, spec, phase, bob, step)
        elif template == "quadruped":
            _draw_quadruped_template(c, spec, phase, bob, step)
        elif template == "bear":
            _draw_bear_template(c, spec, phase, bob, step)
        elif template == "monster":
            _draw_monster_template(c, spec, phase, bob, step)
        elif template == "winged" or body_type == "winged":
            _draw_winged_template(c, spec, phase, bob, step)
        else:
            _draw_humanoid_template(c, spec, phase, bob, step)

        frames.append(c.frame())

    return frames


def _draw_item_sword(c, p, phase):
    glow = int(round((math.sin(phase) + 1) * 2))
    c.ellipse(8, 29, 16, 2, p["shadow"])
    if glow:
        c.line([(9, 6), (22, 19)], p["neon"], width=max(1, glow))
    c.line([(9, 6), (22, 19)], p["outline"], width=4)
    c.line([(10, 6), (22, 18)], p["light"], width=2)
    c.line([(10, 22), (17, 15)], p["outline"], width=3)
    c.line([(20, 20), (25, 25)], p["outline"], width=3)
    c.rect(24, 24, 3, 3, p["outline"])


def _draw_item_shield(c, p):
    c.ellipse(8, 29, 16, 2, p["shadow"])
    c.polygon([(16, 5), (25, 9), (23, 23), (16, 29), (9, 23), (7, 9)], p["outline"])
    c.polygon([(16, 7), (23, 10), (21, 22), (16, 26), (11, 22), (9, 10)], p["mid"])
    c.rect(15, 10, 2, 14, p["light"])
    c.rect(12, 14, 10, 2, p["neon"])


def _draw_item_potion(c, p, phase, spec):
    pulse = int(round((math.sin(phase) + 1) * 2))
    liquid_options = [PURPLE, (80, 190, 120, 255), (220, 70, 120, 255)]
    liquid = liquid_options[_variation(spec, len(liquid_options), 23)]
    c.ellipse(8, 29, 16, 2, p["shadow"])
    c.rect(13, 5, 6, 5, p["outline"])
    c.rect(14, 6, 4, 3, GLASS)
    c.ellipse(9, 9, 14, 18, p["outline"])
    c.ellipse(10, 10, 12, 16, GLASS)
    c.rect(11, 17 - pulse, 10, 8 + pulse, liquid)
    c.rect(13, 12, 4, 2, WHITE)
    _draw_magic_spark(c, 23, 9, phase)


def _draw_item_coin(c, p, phase, spec):
    narrow = abs(int(round(math.sin(phase) * 6)))
    w = max(3, 16 - narrow * 2)
    x = 16 - w // 2
    mark_shift = _variant_shift(spec, 29)
    c.ellipse(8, 29, 16, 2, p["shadow"])
    c.ellipse(x - 1, 6, w + 2, 20, (90, 60, 10, 255))
    c.ellipse(x, 7, w, 18, GOLD)
    if w > 7:
        c.rect(15 + mark_shift, 11, 2, 10, (255, 220, 90, 255))
        c.rect(12, 14 + mark_shift, 8, 2, (150, 95, 15, 255))


def _draw_item_key(c, p, phase):
    c.ellipse(8, 29, 16, 2, p["shadow"])
    c.ellipse(7, 7, 10, 10, (90, 60, 10, 255))
    c.ellipse(9, 9, 6, 6, GOLD)
    c.ellipse(11, 11, 2, 2, (0, 0, 0, 0))
    c.rect(15, 11, 12, 4, GOLD)
    c.rect(23, 15, 2, 4, GOLD)
    c.rect(26, 15, 2, 3, GOLD)
    if math.sin(phase) > 0:
        c.rect(6, 6, 2, 2, (255, 230, 120, 255))


def _draw_item_knife(c, p, phase):
    c.ellipse(8, 29, 16, 2, p["shadow"])
    c.line([(9, 24), (22, 8)], p["outline"], width=4)
    c.line([(10, 23), (22, 8)], (225, 235, 240, 255), width=2)
    c.line([(8, 25), (13, 20)], DARK_BROWN, width=3)
    if math.sin(phase) > 0:
        c.rect(23, 7, 2, 2, p["neon"])


def _draw_item_staff(c, phase):
    c.ellipse(8, 29, 16, 2, (0, 0, 0, 90))
    c.line([(12, 27), (23, 6)], DARK_BROWN, width=3)
    c.line([(13, 27), (23, 6)], (150, 92, 45, 255), width=1)
    c.ellipse(20, 3, 7, 7, BLACK)
    c.ellipse(21, 4, 5, 5, PURPLE)
    _draw_magic_spark(c, 26, 5, phase)


def _draw_item_default(c, p, phase):
    c.ellipse(8, 29, 16, 2, p["shadow"])
    c.polygon([(16, 4), (24, 13), (20, 27), (12, 27), (8, 13)], p["outline"])
    c.polygon([(16, 6), (22, 14), (19, 25), (13, 25), (10, 14)], p["mid"])
    c.polygon([(16, 6), (18, 15), (16, 25), (13, 15)], p["light"])
    if _element_from_template(phase):
        c.rect(25, 20, 2, 2, p["neon"])


def _element_from_template(phase):
    return math.sin(phase) > 0


def generate_generic_item(spec):
    p = PALETTES.get(spec.palette, PALETTES["blue_neon"])
    frames = []

    for i in range(spec.frames):
        phase = (i / max(1, spec.frames)) * math.tau
        c = PixelCanvas(spec.width, spec.height, 32, 32)
        template = _template(spec)

        if template == "sword":
            _draw_item_sword(c, p, phase)
        elif template == "shield":
            _draw_item_shield(c, p)
        elif template == "potion":
            _draw_item_potion(c, p, phase, spec)
        elif template == "coin":
            _draw_item_coin(c, p, phase, spec)
        elif template == "key":
            _draw_item_key(c, p, phase)
        elif template == "knife":
            _draw_item_knife(c, p, phase)
        elif template == "staff":
            _draw_item_staff(c, phase)
        else:
            _draw_item_default(c, p, phase)

        frames.append(c.frame())

    return frames


def _draw_effect_portal(c, p, phase, virtual):
    cx = cy = virtual // 2
    pulse = (math.sin(phase) + 1) / 2
    r1 = int(virtual * 0.22 + pulse * 4)
    r2 = int(virtual * 0.32 + pulse * 3)
    c.ellipse(cx - r2, cy - r2, r2 * 2, r2 * 2, p["outline"])
    c.ellipse(cx - r1, cy - r1, r1 * 2, r1 * 2, p["dark"])
    c.ellipse(cx - r1 + 4, cy - r1 + 4, max(1, r1 * 2 - 8), max(1, r1 * 2 - 8), (0, 0, 0, 0))
    for k in range(10):
        a = phase + (k / 10) * math.tau
        x = cx + int(math.cos(a) * r2)
        y = cy + int(math.sin(a) * r2)
        c.rect(x, y, 2, 2, p["neon"])


def _draw_effect_explosion(c, p, t, virtual):
    cx = cy = virtual // 2
    radius = 3 + int(round(t * virtual * 0.38))
    if t < 0.9:
        c.ellipse(cx - radius, cy - radius, radius * 2, radius * 2, FIRE_OUTLINE)
        c.ellipse(cx - radius + 3, cy - radius + 3, max(2, radius * 2 - 6), max(2, radius * 2 - 6), FIRE_MID)
        c.ellipse(cx - radius // 2, cy - radius // 2, max(2, radius), max(2, radius), FIRE_LIGHT)
    for k in range(8):
        a = (k / 8) * math.tau
        x = cx + int(math.cos(a) * radius * 1.2)
        y = cy + int(math.sin(a) * radius * 1.2)
        c.rect(x, y, 2, 2, p["neon"])


def _draw_effect_flame(c, phase, virtual):
    cx = virtual // 2
    cy = int(virtual * 0.68)
    scale = max(1, virtual // 32)
    _draw_flame(c, cx - 3 * scale, cy - 8 * scale, phase)
    c.ellipse(cx - 8 * scale, cy + 8 * scale, 16 * scale, 3 * scale, (0, 0, 0, 80))


def _draw_effect_glow(c, p, phase, virtual):
    cx = cy = virtual // 2
    pulse = int((math.sin(phase) + 1) * virtual * 0.08)
    c.ellipse(cx - 8 - pulse, cy - 8 - pulse, 16 + pulse * 2, 16 + pulse * 2, p["outline"])
    c.ellipse(cx - 5 - pulse // 2, cy - 5 - pulse // 2, 10 + pulse, 10 + pulse, p["neon"])
    c.rect(cx, cy - 15, 1, 6, p["light"])
    c.rect(cx, cy + 9, 1, 6, p["light"])
    c.rect(cx - 15, cy, 6, 1, p["light"])
    c.rect(cx + 9, cy, 6, 1, p["light"])


def _draw_effect_smoke(c, phase, virtual):
    drift = int(math.sin(phase) * 4)
    c.ellipse(virtual // 2 - 11 + drift, virtual // 2 - 3, 12, 12, SMOKE)
    c.ellipse(virtual // 2 - 3 + drift, virtual // 2 - 10, 15, 15, (115, 118, 124, 165))
    c.ellipse(virtual // 2 + 5 + drift, virtual // 2 - 1, 11, 11, (75, 78, 84, 145))


def generate_generic_effect(spec):
    p = PALETTES.get(spec.palette, PALETTES["purple_neon"])
    frames = []
    virtual = 64 if max(spec.width, spec.height) >= 64 else 32

    for i in range(spec.frames):
        phase = (i / max(1, spec.frames)) * math.tau
        t = i / max(1, spec.frames - 1)
        c = PixelCanvas(spec.width, spec.height, virtual, virtual)
        template = _template(spec)

        if template == "portal":
            _draw_effect_portal(c, p, phase, virtual)
        elif template == "explosion":
            _draw_effect_explosion(c, p, t, virtual)
        elif template == "flame":
            _draw_effect_flame(c, phase, virtual)
        elif template == "smoke":
            _draw_effect_smoke(c, phase, virtual)
        else:
            _draw_effect_glow(c, p, phase, virtual)

        frames.append(c.frame())

    return frames


def _draw_forest_background(c, p):
    c.rect(0, 0, 96, 48, (9, 11, 18, 255))
    c.ellipse(72, 6, 10, 10, p["light"])
    c.ellipse(69, 5, 10, 10, (9, 11, 18, 255))
    c.polygon([(0, 34), (14, 17), (28, 34)], p["dark"])
    c.polygon([(20, 35), (40, 14), (62, 35)], p["dark"])
    c.polygon([(50, 34), (73, 16), (96, 34)], p["dark"])
    for x in range(0, 96, 8):
        h = 8 + (x * 7 % 13)
        c.polygon([(x, 40), (x + 4, 40 - h), (x + 8, 40)], p["outline"])
        c.rect(x + 3, 39, 2, 6, p["outline"])
    c.rect(0, 42, 96, 6, p["outline"])
    c.rect(0, 42, 96, 2, p["mid"])


def _draw_mountain_background(c, p):
    c.rect(0, 0, 96, 48, (14, 18, 28, 255))
    c.ellipse(70, 8, 8, 8, p["light"])
    c.polygon([(0, 40), (23, 14), (47, 40)], p["dark"])
    c.polygon([(30, 40), (58, 10), (96, 40)], p["outline"])
    c.polygon([(50, 19), (58, 10), (67, 19)], p["light"])
    c.rect(0, 40, 96, 8, p["mid"])
    c.rect(0, 44, 96, 4, p["dark"])


def _draw_platformer_ground(c, p):
    c.rect(0, 0, 96, 48, (12, 14, 20, 255))
    for x in range(0, 96, 12):
        c.rect(x, 32 + (x // 12 % 2), 12, 16, p["outline"])
        c.rect(x + 1, 33 + (x // 12 % 2), 10, 14, p["mid"])
        c.rect(x + 2, 34 + (x // 12 % 2), 6, 2, p["light"])
    c.rect(0, 28, 96, 6, p["dark"])
    c.rect(0, 28, 96, 2, p["neon"])


def _draw_tree_background(c, p):
    c.ellipse(8, 24, 16, 3, p["shadow"])
    c.rect(14, 16, 5, 12, DARK_BROWN)
    c.rect(16, 16, 2, 12, BROWN)
    c.ellipse(7, 6, 18, 16, p["outline"])
    c.ellipse(8, 7, 16, 14, p["mid"])
    c.ellipse(11, 8, 8, 5, p["light"])
    c.rect(5, 15, 5, 4, p["mid"])
    c.rect(22, 15, 5, 4, p["dark"])


def _draw_cloud_background(c, p):
    c.rect(0, 0, 32, 32, (0, 0, 0, 0))
    c.ellipse(6, 15, 20, 8, p["shadow"])
    c.ellipse(6, 12, 9, 8, p["white"])
    c.ellipse(12, 8, 10, 11, p["white"])
    c.ellipse(18, 12, 9, 8, p["white"])
    c.rect(9, 15, 15, 5, p["white"])
    c.rect(10, 19, 14, 2, p["light"])


def generate_generic_background(spec):
    p = PALETTES.get(spec.palette, PALETTES["blue_neon"])
    template = _template(spec)

    if template == "tree":
        c = PixelCanvas(spec.width, spec.height, 32, 32)
        _draw_tree_background(c, p)
    elif template == "cloud":
        c = PixelCanvas(spec.width, spec.height, 32, 32)
        _draw_cloud_background(c, p)
    elif template == "mountain":
        c = PixelCanvas(spec.width, spec.height, 128, 64)
        _draw_mountain_background(c, p)
    elif template == "platformer_ground":
        c = PixelCanvas(spec.width, spec.height, 96, 48)
        _draw_platformer_ground(c, p)
    else:
        c = PixelCanvas(spec.width, spec.height, 96, 48)
        _draw_forest_background(c, p)

    return [c.frame()]
