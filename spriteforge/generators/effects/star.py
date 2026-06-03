import math
from ...palettes import PALETTES
from ...draw import PixelCanvas


def generate_star_blink(spec):
    palette = PALETTES.get(spec.palette, PALETTES["blue_neon"])
    frames = []

    for index in range(spec.frames):
        t = index / max(1, spec.frames - 1)
        pulse = math.sin(t * math.pi)
        size = 3 + int(round(pulse * 4))

        canvas = PixelCanvas(spec.width, spec.height, 16, 16)
        p = palette

        cx = 8
        cy = 8

        # brilho externo
        if size >= 5:
            canvas.rect(cx, cy - 7, 1, 3, p["neon"])
            canvas.rect(cx, cy + 5, 1, 3, p["neon"])
            canvas.rect(cx - 7, cy, 3, 1, p["neon"])
            canvas.rect(cx + 5, cy, 3, 1, p["neon"])

        # estrela principal
        canvas.rect(cx, cy - size, 1, size * 2 + 1, p["light"])
        canvas.rect(cx - size, cy, size * 2 + 1, 1, p["light"])

        canvas.rect(cx - 1, cy - 1, 3, 3, p["white"])
        canvas.rect(cx, cy, 1, 1, p["neon"])

        frames.append(canvas.frame())

    return frames
