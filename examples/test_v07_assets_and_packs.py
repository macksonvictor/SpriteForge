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
        "sapo ninja com espada de fogo, 6 frames, 32x32, variacao 2",
        "urso guerreiro com espada, 8 frames, 32x32",
        "goblin com faca, 6 frames, 32x32",
        "dragao voando com fogo, 8 frames, 64x64",
        "moeda girando, 6 frames, 24x24",
        "pocao magica brilhando, 4 frames, 24x24",
        "arvore pixel art, 1 frame, 32x32",
        "chao de grama para plataforma, 1 frame, 96x32",
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
        print("Seed:", metadata["seed"])
        print("Variant:", metadata["variant_id"])

    pack_prompt = "pack sapo ninja com espada de fogo, 32x32"
    print("\nGerando pack:", pack_prompt)
    pack_result = forge.generate_pack(pack_prompt)
    pack_metadata = json.loads(Path(pack_result["metadata"]).read_text(encoding="utf-8"))
    print("Pack:", pack_result["pack_name"])
    print("Output:", pack_result["output_dir"])
    print("Animations:", ", ".join(item["animation"] for item in pack_metadata["animations"]))

    print("\nPreviews gerados:")
    for asset, preview in previews:
        print(f"- {asset}: {preview}")


if __name__ == "__main__":
    main()
