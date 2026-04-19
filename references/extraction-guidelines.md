# Extraction Guidelines

Use this checklist when reading prose and inferring a profile.

## Read for Repetition, Not Just Introduction

Do not build the whole profile from the first description block.

Look for:

- repeated behavioral patterns
- how the character speaks in more than one scene
- how others interpret or describe them
- whether their voice changes between calm and stress

## Infer Voice from Prose Cues

Translate prose into voice traits with conservative mapping.

### Age and timbre

- childlike, small, trembling, squeaky: higher and lighter
- young but composed: clear, mid-high, less breathy
- mature and authoritative: lower, denser, slower
- giant, elder, war-hardened: heavier weight, lower center of gravity

### Register and rhythm

- clipped statements, commands, little filler: firm, controlled rhythm
- many interjections, question marks, emotional spill: lively or unstable rhythm
- polite phrasing and deference: softened edges, cleaner articulation
- slang, rough banter, taunting: sharper consonants, faster flow

### Emotional pressure

- embarrassment or fluster: pitch may rise, pacing may quicken
- menace or authority: slower tempo, darker tone, less pitch variance
- innocence or timidity: lighter onset, hesitation, more fragile contour

## Separate Stable Traits from Scene-Specific States

Store stable voice identity in `voice_design.base_style_prompt`.

Only use `style_variants` for mild presentation changes such as:

- calmer
- more expressive
- closer and softer

Do not encode one-off plot states unless the user explicitly asks for a phase-specific profile.

## Handle Multi-Phase Characters Explicitly

If the manuscript clearly distinguishes stages, split profiles instead of averaging.

Common cases:

- child vs adult
- before vs after transformation
- public persona vs true identity

Name directories so the distinction is obvious:

```text
レシュ_成長前
レシュ_成長後
```

## Write Better `sample_text`

Write one short line the character could naturally say.

Good sample text:

- sounds like an in-world utterance
- includes the character's natural tone
- is easy for TTS to pronounce
- avoids metadata lists and awkward exposition

Avoid:

- lore dumps
- parentheses
- unusually dense punctuation
- long multi-clause narration

## Record Ambiguity

If a trait is plausible but weakly supported:

- leave it out, or
- note it in `misc.notes`

Do not overfit one dramatic scene into the permanent profile.
