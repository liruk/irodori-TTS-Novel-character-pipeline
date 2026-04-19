---
name: irodori-character-pipeline
description: Extract character profile YAML files from novel manuscript markdown and generate Irodori VoiceDesign sample batches. Use when Codex needs to read fiction chapters, infer character traits and speaking style, write profiles in a reusable cache schema, validate them, and call a running Irodori VoiceDesign Gradio server.
---

# Irodori Character Pipeline

## Overview

Use this skill to turn novel chapters into reusable character profile YAML files with `voice_design` metadata, then batch-generate sample voices from those profiles through an external Irodori VoiceDesign server.

Keep the skill focused on two outputs:

1. Character cache files that another repo can reuse
2. Voice sample batches and manifests generated from those cache files

Use this input convention by default:

```text
manuscripts/<world>/<arc-or-chapter>/*.md
```

If the user's workspace already stores manuscripts elsewhere, reuse that layout instead of forcing a move. When doing so, keep the world name and chapter provenance in `source`.

## Workflow

### 1. Inspect the target cache shape

Read existing character cache files in the user workspace before writing anything.

If no suitable examples exist, read [references/profile-schema.md](references/profile-schema.md) and follow that schema.

When the user wants this flow to stay repo-independent, avoid coupling profile generation to the training or inference codebase. Treat the cache and the voice server as separate integration boundaries.

Also inspect where the manuscript source lives. Prefer:

```text
manuscripts/<world>/...
```

If that directory does not exist, use the user's existing manuscript path and do not rewrite the source layout unless asked.

### 2. Extract character evidence from manuscript chapters

Read only the relevant chapter files and gather evidence for:

- apparent age range
- physical scale or species cues
- personality in calm scenes
- personality in combat or stress scenes
- habitual speaking style
- sentence tempo and emotional intensity
- how other characters react to them
- what kind of `sample_text` would sound natural in their voice

Read [references/extraction-guidelines.md](references/extraction-guidelines.md) when the manuscript is long, the characterization is ambiguous, or multiple time phases of the same character exist.

Prefer conservative inferences. If a trait is weakly supported, either omit it or mark the ambiguity in `misc.notes`.

### 3. Write profile YAML files

Write one `profile.yaml` per character directory.

Use the folder layout the user requests, for example:

```text
character_cache/<world>/<character>/profile.yaml
```

Every profile intended for generation must contain `voice_design`.

Prefer:

- `voice_design.group` for output grouping
- `voice_design.base_style_prompt` plus a short `style_variants` list
- `voice_design.sample_text` with one natural in-character line

Keep `sample_text` short, clean, and easy for TTS to read aloud.

### 4. Validate before generating

Run:

```bash
python scripts/validate_profiles.py --character-cache <cache-root>
```

Use the validator before generation whenever:

- new profiles were added
- field names changed
- the cache was moved to a different repo

### 5. Generate voice samples

Run:

```bash
python scripts/generate_voice_samples.py --character-cache <cache-root> --gradio-url <server-url>
```

This script assumes a running Irodori VoiceDesign Gradio server and only depends on the profile cache plus the HTTP API.

Use `--characters` for a partial batch and `--limit` for smoke tests.

## Output Rules

- Keep manuscript-derived facts in `profile`, `background`, `relations`, `source`, and `misc`.
- Keep synthesis-facing instructions inside `voice_design`.
- Do not hardcode repo-specific paths inside YAML except for user-approved grouping names.
- Keep generated audio outside the cache directory.
- Prefer `manuscripts/<world>/...` as the default source layout and `character_cache/<world>/...` as the default output layout.
- If the manuscript source is stored elsewhere, record the actual provenance in `source.evidence`.

## References

- Read [references/profile-schema.md](references/profile-schema.md) for the expected YAML structure.
- Read [references/extraction-guidelines.md](references/extraction-guidelines.md) for how to infer voice traits from prose.

## Scripts

- Use [scripts/validate_profiles.py](scripts/validate_profiles.py) to catch malformed cache files early.
- Use [scripts/generate_voice_samples.py](scripts/generate_voice_samples.py) to batch-call the VoiceDesign server from any repo that has the cache files.
