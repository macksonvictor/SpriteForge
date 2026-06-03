from PIL import Image, ImageDraw


class PixelCanvas:
    """
    Canvas pixel art com coordenadas virtuais de 32x32 ou 48x48.
    Isso permite gerar em 16x16, 32x32, 48x48, 64x64 etc.
    """

    def __init__(self, width, height, virtual_width=32, virtual_height=32):
        self.width = width
        self.height = height
        self.virtual_width = virtual_width
        self.virtual_height = virtual_height
        self.image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        self.draw = ImageDraw.Draw(self.image)

    def sx(self, value):
        return int(round(value * self.width / self.virtual_width))

    def sy(self, value):
        return int(round(value * self.height / self.virtual_height))

    def rect(self, x, y, w, h, color):
        w = max(1, w)
        h = max(1, h)
        x1 = self.sx(x)
        y1 = self.sy(y)
        x2 = self.sx(x + w) - 1
        y2 = self.sy(y + h) - 1
        if x2 < x1:
            x2 = x1
        if y2 < y1:
            y2 = y1
        self.draw.rectangle([x1, y1, x2, y2], fill=color)

    def ellipse(self, x, y, w, h, color):
        w = max(1, w)
        h = max(1, h)
        x1 = self.sx(x)
        y1 = self.sy(y)
        x2 = self.sx(x + w) - 1
        y2 = self.sy(y + h) - 1
        if x2 < x1:
            x2 = x1
        if y2 < y1:
            y2 = y1
        self.draw.ellipse([x1, y1, x2, y2], fill=color)

    def polygon(self, points, color):
        scaled = [(self.sx(x), self.sy(y)) for x, y in points]
        self.draw.polygon(scaled, fill=color)

    def line(self, points, color, width=1):
        scaled = [(self.sx(x), self.sy(y)) for x, y in points]
        self.draw.line(scaled, fill=color, width=max(1, self.sx(width)))

    def frame(self):
        return self.image
