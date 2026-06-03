import math
from ...palettes import PALETTES
from ...draw import PixelCanvas


def generate_sword_glow(spec):
    palette = PALETTES.get(spec.palette, PALETTES["blue_neon"])
    frames = []

    for index in range(spec.frames):
        phase = (index / spec.frames) * math.tau
        glow = int(round((math.sin(phase) + 1) * 1.5))

        canvas = PixelCanvas(spec.width, spec.height, 32, 32)
        p = palette

        # aura
        if glow >= 1:
            canvas.line([(10, 7), (21, 18)], p["neon"], width=glow)
        if glow >= 2:
            canvas.rect(7, 5, 2, 2, p["neon"])
            canvas.rect(23, 20, 2, 2, p["neon"])
            canvas.rect(19, 4, 1, 1, p["light"])

        # lâmina diagonal com contorno
        canvas.line([(9, 6), (22, 19)], p["outline"], width=4)
        canvas.line([(10, 6), (22, 18)], p["light"], width=2)
        canvas.line([(12, 8), (20, 16)], p["white"], width=1)

        # guarda
        canvas.line([(10, 22), (17, 15)], p["outline"], width=3)
        canvas.line([(11, 22), (17, 16)], p["mid"], width=1)

        # cabo
        canvas.line([(20, 20), (25, 25)], p["outline"], width=3)
        canvas.line([(20, 20), (25, 25)], p["dark"], width=1)

        # pomo
        canvas.rect(24, 24, 3, 3, p["outline"])
        canvas.rect(25, 25, 1, 1, p["neon"])

        frames.append(canvas.frame())

    return frames
