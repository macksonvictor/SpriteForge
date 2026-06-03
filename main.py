from spriteforge.core import SpriteForge


def main():
    import sys

    prompt = " ".join(sys.argv[1:]).strip()

    if not prompt:
        prompt = "capivara de armadura andando, 8 frames, 32x32"

    forge = SpriteForge()
    result = forge.generate(prompt)

    print("\nSpriteForge v0.7 concluiu a geração:")
    for key, value in result.items():
        print(f"- {key}: {value}")


if __name__ == "__main__":
    main()
