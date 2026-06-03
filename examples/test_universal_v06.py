import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from spriteforge import SpriteForge


def main():
    forge = SpriteForge()

    prompts = [
        "sapo ninja com espada de fogo, 6 frames, 32x32",
        "capivara de armadura andando, 8 frames, 32x32",
        "urso guerreiro com espada, 8 frames, 32x32",
        "moeda girando, 6 frames, 24x24",
        "pocao magica brilhando, 4 frames, 24x24",
        "portal dimensional roxo girando, 8 frames, 64x64",
        "floresta escura para jogo plataforma, 1 frame, 96x48",
        "dragao voando com fogo, 8 frames, 64x64",
        "monstro de pedra com olhos vermelhos, 6 frames, 32x32",
    ]

    previews = []

    for prompt in prompts:
        print("\nGerando:", prompt)
        result = forge.generate(prompt)
        metadata = json.loads(Path(result["metadata"]).read_text(encoding="utf-8"))
        previews.append((result["asset"], result["preview_gif"]))
        print("Asset:", result["asset"])
        print("Generator:", result["generator"])
        print("Fallback:", result["fallback"])
        print("Template:", metadata["base_template"])
        print("Element:", metadata["element"])

    print("\nPreviews gerados:")
    for asset, preview in previews:
        print(f"- {asset}: {preview}")


if __name__ == "__main__":
    main()
