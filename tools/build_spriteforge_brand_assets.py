from PIL import Image, ImageDraw
from pathlib import Path
import shutil

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BRAND_DIR = PROJECT_ROOT / "assets" / "brand"
BRAND_DIR.mkdir(parents=True, exist_ok=True)

def remove_checkerboard_alpha(img: Image.Image) -> Image.Image:
    img = img.convert("RGBA")
    pix = img.load()
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = pix[x, y]
            if a == 0:
                continue
            mx, mn = max(r, g, b), min(r, g, b)
            sat = mx - mn
            if r > 214 and g > 214 and b > 214 and sat < 22:
                pix[x, y] = (255, 255, 255, 0)
            elif r > 235 and g > 235 and b > 235:
                pix[x, y] = (255, 255, 255, 0)
    return img

def crop_to_content(img: Image.Image, padding=12) -> Image.Image:
    img = img.convert("RGBA")
    bbox = img.getchannel("A").getbbox()
    if not bbox:
        return img
    x0, y0, x1, y1 = bbox
    x0 = max(0, x0 - padding)
    y0 = max(0, y0 - padding)
    x1 = min(img.width, x1 + padding)
    y1 = min(img.height, y1 + padding)
    return img.crop((x0, y0, x1, y1))

def save_scaled_variants(img: Image.Image, stem: str, widths=(1200, 800, 400)):
    img = crop_to_content(remove_checkerboard_alpha(img), padding=20)
    img.save(BRAND_DIR / f"{stem}.png")
    for width in widths:
        ratio = width / img.width
        height = max(1, int(img.height * ratio))
        resized = img.resize((width, height), Image.Resampling.LANCZOS)
        resized.save(BRAND_DIR / f"{stem}_{width}w.png")

def make_square_icon(src: Image.Image, size: int) -> Image.Image:
    src = crop_to_content(remove_checkerboard_alpha(src), padding=20)
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    margin = int(size * 0.12)
    max_size = size - 2 * margin
    scale = min(max_size / src.width, max_size / src.height)
    nw, nh = max(1, int(src.width * scale)), max(1, int(src.height * scale))
    resized = src.resize((nw, nh), Image.Resampling.LANCZOS)
    canvas.alpha_composite(resized, ((size - nw) // 2, (size - nh) // 2))
    return canvas

def build_from_sources(full_logo=None, wordmark=None, icon=None):
    if full_logo:
        save_scaled_variants(Image.open(full_logo), "logo_spriteforge_full")
    if wordmark:
        save_scaled_variants(Image.open(wordmark), "logo_spriteforge_wordmark")
    if icon:
        src = Image.open(icon)
        master = crop_to_content(remove_checkerboard_alpha(src), padding=20)
        master.save(BRAND_DIR / "icon_spriteforge_master.png")
        for size in (16, 24, 32, 48, 64, 128, 256, 512):
            make_square_icon(master, size).save(BRAND_DIR / f"icon_spriteforge_{size}.png")
        make_square_icon(master, 256).save(
            BRAND_DIR / "icon_spriteforge.ico",
            sizes=[(16,16), (24,24), (32,32), (48,48), (64,64), (128,128), (256,256)]
        )
    print("SpriteForge brand assets generated in assets/brand")

if __name__ == "__main__":
    # Put source images in assets/brand/source/ and edit these paths if needed.
    source = BRAND_DIR / "source"
    build_from_sources(
        full_logo=source / "logo_full_source.png" if (source / "logo_full_source.png").exists() else None,
        wordmark=source / "wordmark_source.png" if (source / "wordmark_source.png").exists() else None,
        icon=source / "icon_source.png" if (source / "icon_source.png").exists() else None,
    )
