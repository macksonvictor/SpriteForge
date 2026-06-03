import re
import unicodedata
from .spec import SpriteSpec


def normalize(text: str) -> str:
    text = text.lower().strip()
    text = unicodedata.normalize("NFD", text)
    return "".join(ch for ch in text if unicodedata.category(ch) != "Mn")


def safe_name(text: str) -> str:
    text = normalize(text)
    text = re.sub(r"[^a-z0-9]+", "_", text).strip("_")
    return text[:36] or "asset"


def contains_word(text: str, word: str) -> bool:
    pattern = r"(?<![a-z0-9])" + re.escape(normalize(word)) + r"(?![a-z0-9])"
    return re.search(pattern, text) is not None


def contains_any(text: str, words: list[str]) -> bool:
    return any(contains_word(text, word) for word in words)


CHARACTER_SUBJECTS = [
    ("robot", "character", ["robo", "robô", "robot"]),
    ("slime", "character", ["slime", "gosma", "geleia"]),
]

CREATURE_SUBJECTS = [
    ("sapo", "creature", ["sapo", "frog"]),
    ("capivara", "creature", ["capivara"]),
    ("urso", "creature", ["urso", "bear"]),
    ("cachorro", "creature", ["cachorro", "cao", "cão", "dog"]),
    ("gato", "creature", ["gato", "cat"]),
    ("goblin", "creature", ["goblin"]),
    ("monstro", "creature", ["monstro", "monster"]),
    ("dragao", "creature", ["dragao", "dragão", "dragon"]),
    ("alien", "creature", ["alien"]),
    ("zumbi", "creature", ["zumbi", "zombie"]),
    ("lobo", "creature", ["lobo", "wolf"]),
    ("aranha", "creature", ["aranha", "spider"]),
    ("morcego", "creature", ["morcego", "bat"]),
    ("passaro", "creature", ["passaro", "pássaro", "ave", "bird"]),
    ("fantasma", "creature", ["fantasma", "ghost"]),
]

ITEM_SUBJECTS = [
    ("sword", "item", ["espada", "sword", "lamina", "lâmina"]),
    ("shield", "item", ["escudo", "shield"]),
    ("coin", "item", ["moeda", "coin"]),
    ("potion", "item", ["pocao", "poção", "potion"]),
    ("key", "item", ["chave", "key"]),
    ("knife", "item", ["faca", "adaga", "knife", "dagger"]),
    ("bow", "item", ["arco", "bow"]),
    ("staff", "item", ["cajado", "staff", "vara magica", "vara mágica"]),
    ("axe", "item", ["machado", "axe"]),
    ("item", "item", ["arma", "weapon", "item"]),
]

BACKGROUND_SUBJECTS = [
    ("floresta", "background", ["floresta", "forest"]),
    ("arvore", "background", ["arvore", "árvore", "tree"]),
    ("montanha", "background", ["montanha", "mountain"]),
    ("nuvem", "background", ["nuvem", "cloud"]),
    ("chao", "background", ["chao", "chão", "ground"]),
    ("grama", "background", ["grama", "grass"]),
    ("pedra", "background", ["pedra", "stone", "rocha", "rock"]),
    ("plataforma", "background", ["plataforma", "platform"]),
    ("cidade", "background", ["cidade", "city"]),
    ("castelo", "background", ["castelo", "castle"]),
    ("background", "background", ["cenario", "cenário", "fundo", "background"]),
]

EFFECT_SUBJECTS = [
    ("star", "effect", ["estrela", "star"]),
    ("explosion", "effect", ["explosao", "explosão", "explosion"]),
    ("portal", "effect", ["portal"]),
    ("fire", "effect", ["fogo", "fire", "chama", "flame"]),
    ("ice", "effect", ["gelo", "ice"]),
    ("glow", "effect", ["brilho", "brilhando", "glow", "shine"]),
    ("smoke", "effect", ["fumaca", "fumaça", "smoke"]),
    ("magic", "effect", ["magia", "magica", "mágica", "magic"]),
    ("aura", "effect", ["aura"]),
    ("energy", "effect", ["energia", "energy"]),
    ("ray", "effect", ["raio", "laser"]),
]

FEATURES = [
    ("ninja", ["ninja"]),
    ("warrior", ["guerreiro", "warrior"]),
    ("sword", ["espada", "sword", "lamina", "lâmina"]),
    ("shield", ["escudo", "shield"]),
    ("staff", ["cajado", "staff"]),
    ("knife", ["faca", "adaga", "knife", "dagger"]),
    ("bow", ["arco", "bow"]),
    ("fire", ["fogo", "fire", "chama", "flame"]),
    ("ice", ["gelo", "ice"]),
    ("magic", ["magia", "magica", "mágica", "magic"]),
    ("smoke", ["fumaca", "fumaça", "smoke"]),
    ("armor", ["armadura", "armor"]),
    ("wings", ["asas", "asa", "wing", "wings"]),
    ("horns", ["chifre", "chifres", "horn", "horns"]),
    ("tail", ["cauda", "rabo", "tail"]),
    ("red_eyes", ["olhos vermelhos", "olho vermelho", "red eyes", "red eye"]),
    ("single_eye", ["um olho", "olho unico", "olho único", "single eye"]),
    ("stone", ["pedra", "stone", "rocha", "rock"]),
    ("metal", ["metal", "ferro", "iron", "robotico", "robótico"]),
]


def detect_subject(text: str):
    for subject, category, words in CHARACTER_SUBJECTS:
        if contains_any(text, words):
            return subject, category, True

    for subject, category, words in CREATURE_SUBJECTS:
        if contains_any(text, words):
            return subject, category, True

    for subject, category, words in ITEM_SUBJECTS:
        if contains_any(text, words):
            return subject, category, True

    for subject, category, words in BACKGROUND_SUBJECTS:
        if contains_any(text, words):
            return subject, category, True

    for subject, category, words in EFFECT_SUBJECTS:
        if contains_any(text, words):
            return subject, category, True

    return "asset", "unknown", False


def parse_prompt(prompt: str) -> SpriteSpec:
    text = normalize(prompt)
    subject, category, recognized = detect_subject(text)
    variant_id = detect_variant_id(text)

    action = "idle"
    if contains_any(text, ["correndo", "correr", "run"]):
        action = "run"
    elif contains_any(text, ["andando", "andar", "walk"]):
        action = "walk"
    elif contains_any(text, ["voando", "voar", "fly"]):
        action = "fly"
    elif contains_any(text, ["pulando", "pular", "jump"]):
        action = "jump"
    elif contains_any(text, ["brilhando", "brilho", "glow", "shine"]):
        action = "glow"
    elif contains_any(text, ["piscando", "blink"]):
        action = "blink"
    elif contains_any(text, ["girando", "girar", "spin"]):
        action = "spin"
    elif contains_any(text, ["explodindo", "explodir", "explode"]):
        action = "explode"

    if subject == "robot" and action == "idle":
        action = "run"
    if subject == "slime" and action == "idle":
        action = "jump"
    if subject == "sword" and action == "idle":
        action = "glow"
    if subject == "star" and action == "idle":
        action = "blink"
    if subject == "explosion":
        action = "explode"

    frames = {
        ("robot", "run"): 8,
        ("slime", "jump"): 6,
        ("sword", "glow"): 4,
        ("star", "blink"): 5,
        ("explosion", "explode"): 8,
    }.get((subject, action), 6)
    if category == "background":
        frames = 1

    m = re.search(r"(\d+)\s*frames?", text)
    if m:
        frames = max(1, min(24, int(m.group(1))))

    width, height = 32, 32
    if subject == "star":
        width = height = 16
    if subject == "explosion":
        width = height = 48
    if subject in ["coin", "potion"] and category == "item":
        width = height = 24
    if category == "background":
        width, height = 96, 48

    m = re.search(r"(\d+)\s*x\s*(\d+)", text)
    if m:
        width = max(16, min(256, int(m.group(1))))
        height = max(16, min(256, int(m.group(2))))

    palette = "blue_neon"
    if contains_any(text, ["pedra", "stone", "rocha", "rock", "cinza", "metal", "ferro", "iron"]):
        palette = "stone"
    elif contains_any(text, ["roxo", "purple", "portal", "dimensional"]):
        palette = "purple_neon"
    elif contains_any(text, ["verde", "green", "sapo", "slime", "floresta", "grama"]):
        palette = "green_neon"
    elif contains_any(text, ["fogo", "fire", "laranja"]):
        palette = "fire"
    elif contains_any(text, ["vermelho", "red", "olhos vermelhos"]):
        palette = "red_neon"
    elif contains_any(text, ["azul", "blue", "gelo", "neon"]):
        palette = "blue_neon"

    features = []
    for feature, words in FEATURES:
        if contains_any(text, words):
            features.append(feature)

    name = f"{safe_name(subject)}_{action}_{width}x{height}_{frames}frames"
    if variant_id is not None:
        name = f"{name}_v{variant_id:03d}"

    return SpriteSpec(
        subject=subject,
        action=action,
        frames=frames,
        width=width,
        height=height,
        palette=palette,
        name=name,
        category=category,
        features=features,
        raw_prompt=prompt,
        is_fallback=False,
        is_unknown=not recognized,
        variant_id=variant_id,
    )


def detect_variant_id(text: str) -> int | None:
    match = re.search(r"\b(?:variacao|variante|variant|variation|var|v)\s*0*(\d+)\b", text)
    if not match:
        return None
    return max(1, min(999, int(match.group(1))))
