import math
from ...palettes import PALETTES
from ...draw import PixelCanvas


def generate_slime_jump(spec):
    palette = PALETTES.get(spec.palette, PALETTES["green_neon"])
    if spec.palette == "blue_neon":
        palette = PALETTES["green_neon"]

    frames = []

    for index in range(spec.frames):
        t = index / max(1, spec.frames - 1)
        jump = math.sin(t * math.pi)
        y_offset = -int(round(jump * 7))
        squash = math.sin(t * math.tau)

        body_w = 18 + int(round(max(0, -squash) * 3))
        body_h = 13 + int(round(max(0, squash) * 3))
        x = 16 - body_w // 2
        y = 17 - body_h // 2 + y_offset

        canvas = PixelCanvas(spec.width, spec.height, 32, 32)
        p = palette

        # sombra muda com altura do pulo
        shadow_w = 18 - int(round(jump * 6))
        canvas.ellipse(16 - shadow_w // 2, 28, shadow_w, 3, p["shadow"])

        # contorno e corpo
        canvas.ellipse(x - 1, y - 1, body_w + 2, body_h + 2, p["outline"])
        canvas.ellipse(x, y, body_w, body_h, p["mid"])

        # topo brilhante
        canvas.ellipse(x + 4, y + 2, body_w - 8, 4, p["light"])

        # base escura
        canvas.ellipse(x + 3, y + body_h - 5, body_w - 6, 4, p["dark"])

        # olhos
        eye_y = y + 6
        canvas.rect(x + 6, eye_y, 2, 2, p["eye"])
        canvas.rect(x + body_w - 8, eye_y, 2, 2, p["eye"])

        # boca
        if jump > 0.55:
            canvas.rect(15, y + 10, 2, 1, p["outline"])
        else:
            canvas.rect(14, y + 10, 4, 1, p["outline"])

        # gotinha/energia ao subir
        if jump > 0.45:
            canvas.rect(9, y + body_h + 1, 2, 2, p["neon"])
            canvas.rect(22, y + body_h, 1, 1, p["neon"])

        frames.append(canvas.frame())

    return frames
