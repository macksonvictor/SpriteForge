import math
from ...palettes import PALETTES
from ...draw import PixelCanvas


def generate_explosion_fire(spec):
    palette = PALETTES["fire"]
    frames = []

    for index in range(spec.frames):
        t = index / max(1, spec.frames - 1)
        radius = 3 + int(round(t * 18))
        fade_stage = t

        canvas = PixelCanvas(spec.width, spec.height, 48, 48)
        p = palette

        cx = 24
        cy = 24

        # fumaça/sombra nos últimos frames
        if fade_stage > 0.55:
            smoke = (70, 70, 70, int(180 * (1 - fade_stage)))
            canvas.ellipse(cx - radius, cy - radius // 2, radius * 2, radius, smoke)

        # núcleo
        if fade_stage < 0.85:
            canvas.ellipse(cx - radius, cy - radius, radius * 2, radius * 2, p["outline"])
            canvas.ellipse(cx - radius + 3, cy - radius + 3, radius * 2 - 6, radius * 2 - 6, p["dark"])
            canvas.ellipse(cx - radius // 2, cy - radius // 2, radius, radius, p["mid"])
            canvas.ellipse(cx - radius // 4, cy - radius // 4, max(2, radius // 2), max(2, radius // 2), p["light"])

        # raios triangulares
        if fade_stage < 0.8:
            points = [
                [(cx, cy - radius - 5), (cx - 3, cy - radius // 2), (cx + 3, cy - radius // 2)],
                [(cx + radius + 5, cy), (cx + radius // 2, cy - 3), (cx + radius // 2, cy + 3)],
                [(cx, cy + radius + 5), (cx - 3, cy + radius // 2), (cx + 3, cy + radius // 2)],
                [(cx - radius - 5, cy), (cx - radius // 2, cy - 3), (cx - radius // 2, cy + 3)],
            ]
            for poly in points:
                canvas.polygon(poly, p["light"])

        # partículas
        for i in range(8):
            angle = (i / 8) * math.tau
            dist = int(radius * 1.15)
            px = cx + int(math.cos(angle) * dist)
            py = cy + int(math.sin(angle) * dist)
            color = p["neon"] if i % 2 == 0 else p["light"]
            if fade_stage < 0.95:
                canvas.rect(px, py, 2, 2, color)

        frames.append(canvas.frame())

    return frames
