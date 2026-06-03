import hashlib
import json
import re
from datetime import datetime
from pathlib import Path

from .parser import normalize, parse_prompt, safe_name
from .planner import build_asset_plan
from .render import save_frames, save_preview_gif, save_spritesheet

from .generators.characters.robot import generate_robot_run
from .generators.characters.slime import generate_slime_jump
from .generators.effects.explosion import generate_explosion_fire
from .generators.effects.star import generate_star_blink
from .generators.generic.all import (
    generate_generic_background,
    generate_generic_creature,
    generate_generic_effect,
    generate_generic_item,
)
from .generators.items.sword import generate_sword_glow


PACK_ACTIONS = [
    ("idle", 4),
    ("walk", 8),
    ("jump", 6),
    ("attack", 6),
]


class SpriteForge:
    def __init__(self, output_root="outputs"):
        self.output_root = Path(output_root)
        self.output_root.mkdir(parents=True, exist_ok=True)

    def generate(self, prompt: str, seed: int | None = None, variant_id: int | None = None):
        if self._is_pack_prompt(prompt):
            return self.generate_pack(prompt, seed=seed, variant_id=variant_id)

        spec = self._prepare_spec(prompt, seed=seed, variant_id=variant_id)
        generator, generator_name = self._select_generator(spec)
        output_dir = self.output_root / spec.name
        result = self._write_asset(
            spec=spec,
            prompt=prompt,
            generator=generator,
            generator_name=generator_name,
            output_dir=output_dir,
            asset_name=spec.name,
        )

        if spec.is_unknown:
            self._log_unknown_request(spec, generator_name)

        return result

    def generate_pack(self, prompt: str, seed: int | None = None, variant_id: int | None = None):
        clean_prompt = self._clean_pack_prompt(prompt)
        base_spec = self._prepare_spec(clean_prompt, seed=seed, variant_id=variant_id)
        base_plan = base_spec.asset_plan
        pack_name = self._pack_name(base_plan)
        pack_dir = self.output_root / "packs" / pack_name
        pack_dir.mkdir(parents=True, exist_ok=True)

        animations = []
        for index, (action, frames) in enumerate(PACK_ACTIONS):
            spec = self._prepare_spec(
                clean_prompt,
                seed=(base_spec.seed or 0) + index + 1,
                variant_id=base_spec.variant_id,
                action=action,
                frames=frames,
            )
            generator, generator_name = self._select_generator(spec)
            action_dir = pack_dir / action
            asset_name = f"{pack_name}_{action}"
            result = self._write_asset(
                spec=spec,
                prompt=prompt,
                generator=generator,
                generator_name=generator_name,
                output_dir=action_dir,
                asset_name=asset_name,
                metadata_extra={
                    "pack_name": pack_name,
                    "animation": action,
                },
            )
            animations.append(
                {
                    "animation": action,
                    "asset": asset_name,
                    "generator": generator_name,
                    "output_dir": result["output_dir"],
                    "spritesheet": result["spritesheet"],
                    "preview_gif": result["preview_gif"],
                    "metadata": result["metadata"],
                }
            )

        pack_metadata = {
            "spriteforge_version": "0.7",
            "prompt": prompt,
            "pack_name": pack_name,
            "category": base_spec.category,
            "asset_family": base_plan.asset_family,
            "subject": base_spec.subject,
            "body_type": base_plan.body_type,
            "base_template": base_plan.base_template,
            "features": base_plan.features,
            "accessories": base_plan.accessories,
            "element": base_plan.element,
            "seed": base_spec.seed,
            "variant_id": base_spec.variant_id,
            "animations": animations,
            "quality_notes": (
                f"Generated character pack using {base_plan.base_template} template "
                f"with {len(animations)} animations."
            ),
        }
        pack_metadata_path = pack_dir / f"{pack_name}.json"
        pack_metadata_path.write_text(json.dumps(pack_metadata, indent=4, ensure_ascii=False), encoding="utf-8")

        return {
            "asset": pack_name,
            "generator": "pack.creature",
            "fallback": "True",
            "is_pack": "True",
            "output_dir": str(pack_dir),
            "frames": str(pack_dir),
            "spritesheet": animations[0]["spritesheet"],
            "preview_gif": animations[0]["preview_gif"],
            "metadata": str(pack_metadata_path),
            "pack_name": pack_name,
            "animations": animations,
        }

    def _prepare_spec(
        self,
        prompt: str,
        seed: int | None = None,
        variant_id: int | None = None,
        action: str | None = None,
        frames: int | None = None,
    ):
        spec = parse_prompt(prompt)

        if action:
            spec.action = action
        if frames:
            spec.frames = frames

        if variant_id is not None:
            spec.variant_id = max(1, min(999, int(variant_id)))

        spec.seed = seed if seed is not None else self._seed_for(prompt, spec.variant_id)
        spec.name = self._name_for(spec)
        spec.asset_plan = build_asset_plan(spec)
        return spec

    def _write_asset(
        self,
        spec,
        prompt: str,
        generator,
        generator_name: str,
        output_dir: Path,
        asset_name: str,
        metadata_extra: dict | None = None,
    ):
        frames = generator(spec)
        output_dir.mkdir(parents=True, exist_ok=True)

        frame_paths = save_frames(frames, output_dir)
        spritesheet_path = save_spritesheet(frames, output_dir, asset_name)
        gif_path = save_preview_gif(frames, output_dir, asset_name)

        metadata = self._metadata(
            spec=spec,
            prompt=prompt,
            generator_name=generator_name,
            asset_name=asset_name,
            frame_paths=frame_paths,
            spritesheet_path=spritesheet_path,
            gif_path=gif_path,
        )
        if metadata_extra:
            metadata.update(metadata_extra)

        metadata_path = output_dir / f"{asset_name}.json"
        metadata_path.write_text(json.dumps(metadata, indent=4, ensure_ascii=False), encoding="utf-8")

        return {
            "asset": asset_name,
            "generator": generator_name,
            "fallback": str(spec.is_fallback),
            "is_pack": "False",
            "output_dir": str(output_dir),
            "frames": str(output_dir / "frames"),
            "spritesheet": str(spritesheet_path),
            "preview_gif": str(gif_path),
            "metadata": str(metadata_path),
        }

    def _metadata(self, spec, prompt, generator_name, asset_name, frame_paths, spritesheet_path, gif_path):
        plan = spec.asset_plan
        return {
            "spriteforge_version": "0.7",
            "prompt": prompt,
            "category": spec.category,
            "asset_family": plan.asset_family,
            "subject": spec.subject,
            "body_type": plan.body_type,
            "base_template": plan.base_template,
            "action": spec.action,
            "features": plan.features,
            "accessories": plan.accessories,
            "element": plan.element,
            "generator": generator_name,
            "fallback": spec.is_fallback,
            "seed": spec.seed,
            "variant_id": spec.variant_id,
            "quality_notes": self._quality_notes(spec, plan, generator_name),
            "animation_style": plan.animation_style,
            "frames": spec.frames,
            "size": list(plan.size),
            "palette": plan.palette,
            "palette_key": spec.palette,
            "name": asset_name,
            "frame_files": [str(path) for path in frame_paths],
            "spritesheet": str(spritesheet_path),
            "preview_gif": str(gif_path),
        }

    def _select_generator(self, spec):
        if spec.subject == "robot" and spec.action == "run":
            return generate_robot_run, "specific.robot_run"
        if spec.subject == "slime" and spec.action == "jump":
            return generate_slime_jump, "specific.slime_jump"
        if spec.subject == "sword" and spec.action == "glow":
            return generate_sword_glow, "specific.sword_glow"
        if spec.subject == "star" and spec.action == "blink":
            return generate_star_blink, "specific.star_blink"
        if spec.subject == "explosion" and spec.action == "explode":
            return generate_explosion_fire, "specific.explosion_fire"

        spec.is_fallback = True

        if spec.category in ["creature", "character"]:
            return generate_generic_creature, "generic.creature"
        if spec.category == "item":
            return generate_generic_item, "generic.item"
        if spec.category == "effect":
            return generate_generic_effect, "generic.effect"
        if spec.category == "background":
            return generate_generic_background, "generic.background"

        return generate_generic_creature, "generic.creature"

    def _quality_notes(self, spec, plan, generator_name):
        readable_generator = generator_name.replace(".", " ")
        if generator_name.startswith("generic."):
            note = f"Generated with {readable_generator} fallback."
        else:
            note = f"Generated with {readable_generator} generator."

        if spec.is_unknown:
            return f"{note} Subject/category could not be identified confidently."

        layers = []
        if plan.features:
            layers.append(f"features {', '.join(plan.features)}")
        if plan.accessories:
            layers.append(f"accessories {', '.join(plan.accessories)}")
        if plan.element != "none":
            layers.append(f"element {plan.element}")
        if spec.variant_id is not None:
            layers.append(f"variant v{spec.variant_id:03d}")

        if layers:
            return (
                f"{note} Subject detected as {spec.subject} using "
                f"{plan.base_template} template with {'; '.join(layers)}."
            )

        return f"{note} Subject detected as {spec.subject} using {plan.base_template} template."

    def _log_unknown_request(self, spec, generator_name):
        log_dir = Path("spriteforge") / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / "unknown_requests.jsonl"

        row = {
            "time": datetime.now().isoformat(),
            "prompt": spec.raw_prompt,
            "subject": spec.subject,
            "category": spec.category,
            "action": spec.action,
            "features": spec.features,
            "generator_used": generator_name,
            "seed": spec.seed,
            "variant_id": spec.variant_id,
        }

        with log_path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(row, ensure_ascii=False) + "\n")

    def _seed_for(self, prompt: str, variant_id: int | None):
        payload = f"{normalize(prompt)}|{variant_id or 0}"
        digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        return int(digest[:12], 16)

    def _name_for(self, spec):
        name = f"{safe_name(spec.subject)}_{spec.action}_{spec.width}x{spec.height}_{spec.frames}frames"
        if spec.variant_id is not None:
            name = f"{name}_v{spec.variant_id:03d}"
        return name

    def _pack_name(self, plan):
        parts = [plan.subject]
        parts.extend(plan.features)
        if plan.element != "none":
            parts.append(plan.element)
        parts.extend(self._pack_accessory_name(accessory) for accessory in plan.accessories)
        return safe_name("_".join(part for part in parts if part))

    def _pack_accessory_name(self, accessory):
        names = {
            "armor_plate": "armor",
            "ninja_band": "ninja",
        }
        return names.get(accessory, accessory)

    def _is_pack_prompt(self, prompt: str):
        return normalize(prompt).startswith("pack ")

    def _clean_pack_prompt(self, prompt: str):
        return re.sub(r"^\s*pack\b[:\s-]*", "", prompt, count=1, flags=re.IGNORECASE).strip()
