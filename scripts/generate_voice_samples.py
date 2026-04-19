#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import httpx
import json
import re
import shutil
import sys
import unicodedata
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import yaml
from gradio_client import Client

DEFAULT_CHECKPOINT = "Aratako/Irodori-TTS-500M-v2-VoiceDesign"
DEFAULT_GRADIO_URL = "http://127.0.0.1:7861/"
DEFAULT_OUTPUT_ROOT = Path("generated_character_samples")


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


class VoiceDesignClient(Client):
    """Compatibility layer for newer Gradio apps mounted under /gradio_api."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        api_prefix = str(self.config.get("api_prefix") or "/gradio_api").rstrip("/")
        base = self.src.rstrip("/")
        for attr in ("api_url", "sse_url", "sse_data_url", "reset_url"):
            value = getattr(self, attr, None)
            if isinstance(value, str) and value.startswith(base) and api_prefix not in value:
                setattr(self, attr, value.replace(base, f"{base}{api_prefix}", 1))

    def _get_api_info(self):
        url = self.src.rstrip("/") + "/gradio_api/info"
        response = httpx.get(url, headers=self.headers, cookies=self.cookies, verify=self.ssl_verify)
        if response.is_success:
            return response.json()
        raise ValueError(f"Could not fetch api info for {self.src}: {response.text}")


@dataclass
class CharacterConfig:
    name: str
    reading: str
    text: str
    style_prompts: list[str]
    group: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Batch-generate Irodori VoiceDesign samples from reusable profile YAML files.")
    parser.add_argument("--character-cache", type=Path, required=True)
    parser.add_argument("--gradio-url", default=DEFAULT_GRADIO_URL)
    parser.add_argument("--checkpoint", default=DEFAULT_CHECKPOINT)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--characters", nargs="*")
    parser.add_argument("--steps", type=int, default=20)
    parser.add_argument("--model-device", default="cuda")
    parser.add_argument("--codec-device", default="cuda")
    parser.add_argument("--model-precision", default="bf16")
    parser.add_argument("--codec-precision", default="bf16")
    parser.add_argument("--cfg-guidance-mode", default="independent")
    parser.add_argument("--cfg-scale-text", type=float, default=2.0)
    parser.add_argument("--cfg-scale-caption", type=float, default=4.0)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--limit", type=int, default=0)
    return parser.parse_args()


def sanitize_filename(text: str, max_len: int = 120) -> str:
    normalized = unicodedata.normalize("NFKC", text).strip()
    normalized = re.sub(r"[<>:\"/\\\\|?*\r\n\t]+", "-", normalized)
    normalized = re.sub(r"\s+", " ", normalized)
    normalized = re.sub(r"-{2,}", "-", normalized)
    normalized = normalized.strip(" .-")
    if not normalized:
        normalized = "sample"
    if len(normalized) > max_len:
        normalized = normalized[:max_len].rstrip(" .-")
    return normalized


def parse_seed(log_text: str) -> int | None:
    match = re.search(r"seed_used:\s*(\d+)", log_text)
    return int(match.group(1)) if match else None


def load_character_configs(cache_dir: Path, selected_names: set[str] | None) -> list[CharacterConfig]:
    configs: list[CharacterConfig] = []
    for yaml_path in sorted(cache_dir.rglob("*.yaml")):
        data = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or "voice_design" not in data:
            continue

        name = str(data["name"])
        if selected_names and name not in selected_names:
            continue

        voice_design = data["voice_design"]
        reading = str(data.get("reading") or name)
        text = str(voice_design.get("sample_text") or voice_design.get("text") or reading)
        group = str(voice_design.get("group") or yaml_path.parent.relative_to(cache_dir).as_posix())

        prompts = voice_design.get("style_prompts")
        if isinstance(prompts, list) and prompts:
            style_prompts = [str(item).strip() for item in prompts if str(item).strip()]
        else:
            base_prompt = str(voice_design.get("base_style_prompt") or "").strip()
            variants = voice_design.get("style_variants") or []
            if not base_prompt:
                raise KeyError(f"{yaml_path}: missing voice_design.base_style_prompt")
            if variants:
                style_prompts = [f"{base_prompt} {str(item).strip()}".strip() for item in variants]
            else:
                style_prompts = [base_prompt]

        configs.append(CharacterConfig(name=name, reading=reading, text=text, style_prompts=style_prompts, group=group))
    return configs


def run_generation(
    client: VoiceDesignClient,
    checkpoint: str,
    config: CharacterConfig,
    style_prompt: str,
    args: argparse.Namespace,
) -> tuple[Path, str, int | None]:
    result = client.predict(
        checkpoint,
        args.model_device,
        args.model_precision,
        args.codec_device,
        args.codec_precision,
        config.text,
        style_prompt,
        args.steps,
        1,
        "",
        args.cfg_guidance_mode,
        args.cfg_scale_text,
        args.cfg_scale_caption,
        "",
        0.5,
        1.0,
        True,
        "",
        "",
        "",
        "",
        "",
        api_name="/_run_generation",
    )
    first = result[0]["value"]
    audio_path = Path(first["path"] if isinstance(first, dict) else first)
    log_text = result[-2]
    return audio_path, log_text, parse_seed(log_text)


def main() -> int:
    args = parse_args()
    selected_names = set(args.characters) if args.characters else None
    configs = load_character_configs(args.character_cache, selected_names)
    if not configs:
        raise SystemExit("No matching voice_design profiles were found.")

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_root = args.output_root / stamp
    out_root.mkdir(parents=True, exist_ok=True)
    manifest_jsonl = out_root / "manifest.jsonl"
    manifest_csv = out_root / "manifest.csv"

    client = VoiceDesignClient(args.gradio_url, download_files=False)

    rows: list[dict[str, object]] = []
    generated_count = 0
    stop_early = False

    for config in configs:
        character_dir = out_root / Path(config.group) / sanitize_filename(config.name, max_len=80)
        character_dir.mkdir(parents=True, exist_ok=True)

        for index, style_prompt in enumerate(config.style_prompts, start=1):
            filename = sanitize_filename(f"{config.name}__{style_prompt}", max_len=140) + ".wav"
            destination = character_dir / filename
            if destination.exists() and not args.overwrite:
                print(f"[skip] {destination}")
                continue

            print(f"[generate] {config.name} [{index}/{len(config.style_prompts)}]")
            audio_path, log_text, seed = run_generation(client, args.checkpoint, config, style_prompt, args)
            shutil.copy2(audio_path, destination)

            row = {
                "character_name": config.name,
                "reading": config.reading,
                "index": index,
                "text": config.text,
                "style_prompt": style_prompt,
                "seed": seed,
                "output_path": str(destination.resolve()),
            }
            rows.append(row)
            with manifest_jsonl.open("a", encoding="utf-8") as fp:
                fp.write(json.dumps(row, ensure_ascii=False) + "\n")

            generated_count += 1
            print(f"[saved] {destination}")
            if log_text:
                print(log_text.splitlines()[0])

            if args.limit and generated_count >= args.limit:
                stop_early = True
                break

        if stop_early:
            break

    with manifest_csv.open("w", newline="", encoding="utf-8-sig") as fp:
        writer = csv.DictWriter(
            fp,
            fieldnames=["character_name", "reading", "index", "text", "style_prompt", "seed", "output_path"],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(
        json.dumps(
            {
                "generated_files": generated_count,
                "output_dir": str(out_root.resolve()),
                "manifest_jsonl": str(manifest_jsonl.resolve()),
                "manifest_csv": str(manifest_csv.resolve()),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
