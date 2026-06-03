import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from spriteforge import SpriteForge

forge = SpriteForge()

prompts = [
    "robo correndo, 8 frames, 32x32, azul neon",
    "slime verde pulando, 6 frames, 32x32",
    "espada magica brilhando, 4 frames, 32x32, azul",
    "estrela piscando, 5 frames, 16x16",
    "explosao de fogo, 8 frames, 48x48",
    "capivara de armadura andando, 8 frames, 32x32",
    "sapo ninja com espada de fogo, 6 frames, 32x32",
    "portal dimensional roxo girando, 8 frames, 64x64",
    "monstro de pedra com olhos vermelhos, 6 frames, 32x32",
    "floresta escura para jogo plataforma, 1 frame, 96x48",
]

for prompt in prompts:
    print("\nGerando:", prompt)
    result = forge.generate(prompt)
    print("Generator:", result["generator"])
    print("Fallback:", result["fallback"])
    print("Preview:", result["preview_gif"])
