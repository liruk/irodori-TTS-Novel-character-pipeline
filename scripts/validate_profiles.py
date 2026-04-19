#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

REQUIRED_TOP_LEVEL = {
    "name",
    "reading",
    "profile",
    "background",
    "relations",
    "voice_design",
}

REQUIRED_VOICE_DESIGN = {
    "group",
    "sample_text",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate reusable character profile YAML files.")
    parser.add_argument("--character-cache", type=Path, required=True)
    return parser.parse_args()


def validate_profile(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - defensive
        return [f"{path}: failed to parse YAML: {exc}"]

    if not isinstance(data, dict):
        return [f"{path}: root must be a mapping"]

    missing = REQUIRED_TOP_LEVEL - set(data.keys())
    if missing:
        errors.append(f"{path}: missing top-level keys: {', '.join(sorted(missing))}")

    voice_design = data.get("voice_design")
    if not isinstance(voice_design, dict):
        errors.append(f"{path}: voice_design must be a mapping")
    else:
        missing_voice = REQUIRED_VOICE_DESIGN - set(voice_design.keys())
        if missing_voice:
            errors.append(f"{path}: missing voice_design keys: {', '.join(sorted(missing_voice))}")
        has_style_prompts = isinstance(voice_design.get("style_prompts"), list) and bool(voice_design.get("style_prompts"))
        has_base_prompt = bool(str(voice_design.get("base_style_prompt") or "").strip())
        if not (has_style_prompts or has_base_prompt):
            errors.append(f"{path}: voice_design needs style_prompts or base_style_prompt")

    relations = data.get("relations")
    if not isinstance(relations, list):
        errors.append(f"{path}: relations must be a list")

    background = data.get("background")
    if not isinstance(background, list):
        errors.append(f"{path}: background must be a list")

    return errors


def main() -> int:
    args = parse_args()
    cache_dir = args.character_cache
    yaml_files = sorted(cache_dir.rglob("*.yaml"))
    if not yaml_files:
        print(f"No YAML files found under {cache_dir}")
        return 1

    errors: list[str] = []
    for path in yaml_files:
        errors.extend(validate_profile(path))

    if errors:
        for error in errors:
            print(error)
        print(f"\nValidation failed: {len(errors)} issue(s)")
        return 1

    print(f"Validated {len(yaml_files)} profile file(s) under {cache_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
