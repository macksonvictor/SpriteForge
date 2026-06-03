import math
from ...palettes import PALETTES
from ...draw import PixelCanvas


def generate_robot_run(spec):
    palette = PALETTES.get(spec.palette, PALETTES["blue_neon"])
    frames = []

    for index in range(spec.frames):
        phase = (index / spec.frames) * math.tau

        canvas = PixelCanvas(spec.width, spec.height, 32, 32)
        p = palette

        bob = int(round(math.sin(phase) * 1))
        arm_a = int(round(math.sin(phase) * 2))
        arm_b = -arm_a
        leg_a = int(round(math.sin(phase) * 3))
        leg_b = -leg_a

        # sombra
        canvas.ellipse(8, 29, 16, 2, p["shadow"])

        # rastro neon
        if index % 2 == 0:
            canvas.rect(4, 17 + bob, 3, 1, p["neon"])
            canvas.rect(2, 19 + bob, 2, 1, p["neon"])
        else:
            canvas.rect(5, 18 + bob, 3, 1, p["neon"])
            canvas.rect(3, 20 + bob, 1, 1, p["neon"])

        # propulsor/mochila
        canvas.rect(8, 13 + bob, 3, 8, p["outline"])
        canvas.rect(9, 14 + bob, 2, 6, p["dark"])

        # antena
        canvas.rect(15, 3 + bob, 2, 3, p["outline"])
        canvas.rect(15, 2 + bob, 2, 1, p["neon"])

        # cabeça
        canvas.rect(11, 6 + bob, 10, 8, p["outline"])
        canvas.rect(12, 7 + bob, 8, 6, p["mid"])
        canvas.rect(13, 8 + bob, 5, 2, p["light"])
        canvas.rect(18, 9 + bob, 2, 2, p["eye"])

        # pescoço
        canvas.rect(14, 14 + bob, 4, 2, p["outline"])
        canvas.rect(15, 14 + bob, 2, 2, p["dark"])

        # tronco
        canvas.rect(10, 16 + bob, 12, 8, p["outline"])
        canvas.rect(11, 17 + bob, 10, 6, p["dark"])
        canvas.rect(13, 18 + bob, 5, 2, p["mid"])
        canvas.rect(18, 18 + bob, 2, 2, p["neon"])

        # braços
        canvas.rect(8, 17 + bob + arm_a, 3, 3, p["outline"])
        canvas.rect(7, 19 + bob + arm_a, 3, 5, p["mid"])
        canvas.rect(6, 23 + bob + arm_a, 3, 2, p["outline"])

        canvas.rect(21, 17 + bob + arm_b, 3, 3, p["outline"])
        canvas.rect(22, 19 + bob + arm_b, 3, 5, p["mid"])
        canvas.rect(23, 23 + bob + arm_b, 3, 2, p["outline"])

        # pernas
        canvas.rect(11, 24 + bob, 3, 3, p["outline"])
        canvas.rect(10 + leg_a, 26 + bob, 4, 3, p["mid"])
        canvas.rect(9 + leg_a, 28 + bob, 5, 2, p["outline"])

        canvas.rect(18, 24 + bob, 3, 3, p["outline"])
        canvas.rect(18 + leg_b, 26 + bob, 4, 3, p["mid"])
        canvas.rect(18 + leg_b, 28 + bob, 5, 2, p["outline"])

        frames.append(canvas.frame())

    return frames
