from pathlib import Path
from PIL import Image


def save_frames(frames, output_dir: Path):
    frames_dir = output_dir / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)

    paths = []

    for index, frame in enumerate(frames, start=1):
        path = frames_dir / f"frame_{index:02d}.png"
        frame.save(path)
        paths.append(path)

    return paths


def save_spritesheet(frames, output_dir: Path, name: str):
    width, height = frames[0].size
    sheet = Image.new("RGBA", (width * len(frames), height), (0, 0, 0, 0))

    for index, frame in enumerate(frames):
        sheet.paste(frame, (index * width, 0))

    path = output_dir / f"{name}_spritesheet.png"
    sheet.save(path)
    return path


def save_preview_gif(frames, output_dir: Path, name: str, scale: int = 6):
    scaled = []

    for frame in frames:
        bigger = frame.resize(
            (frame.width * scale, frame.height * scale),
            Image.Resampling.NEAREST
        )
        scaled.append(bigger)

    path = output_dir / f"{name}_preview.gif"

    scaled[0].save(
        path,
        save_all=True,
        append_images=scaled[1:],
        duration=100,
        loop=0,
        disposal=2
    )

    return path
