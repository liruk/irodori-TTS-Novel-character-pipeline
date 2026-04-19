# Profile Schema

Write one `profile.yaml` per character directory.

Minimum recommended structure:

```yaml
name: Character Name
reading: かな
aliases:
  - Alias
profile:
  age: "10代後半"
  appearance: 外見の要約
  personality: 性格の要約
  ability:
    - 主要能力
  speech_style: 口調の要約
background:
  - 生い立ちや立場
relations:
  - target: Other Character
    content: 関係性の要約
voice_design:
  group: WorldName/arc-name
  base_style_prompt: >
    地声の高さ、柔らかさ、勢い、年齢感、種族感、威圧感などをまとめた短いプロンプト。
  style_variants:
    - 落ち着いて聞き取りやすく、抑揚を丁寧につける。
    - やや感情を強めに乗せ、キャラクターらしい表情をはっきり出す。
    - 近い距離で語りかけるように、息遣いを少しだけ柔らかくする。
  sample_text: 本人らしい短い台詞
source:
  chapters:
    - chapter1
  evidence:
    - chapter1/08.md:13-24
misc:
  stage: chapter1
  notes: 補足
```

## Field Guidance

### `profile`

Store stable character traits that a human editor would expect to reuse.

- `age`: use a range or stage if exact age is unknown
- `appearance`: prioritize body scale, species, silhouette, and visual age
- `personality`: prefer traits shown repeatedly across scenes
- `ability`: keep it short and list-like
- `speech_style`: summarize register, tempo, roughness, politeness, and emotional intensity

### `voice_design`

Store only synthesis-facing instructions.

- `group`: output grouping path below the generation timestamp directory
- `base_style_prompt`: 1-2 sentences, compact and descriptive
- `style_variants`: usually 3 variants are enough for auditioning
- `sample_text`: write a line that sounds natural for the character, not a metadata dump

### `source`

Keep a lightweight audit trail.

- `chapters`: chapter names or arc names
- `evidence`: file and line anchors when available

## Naming and Layout

Prefer this directory layout when sharing the cache between repos:

```text
character_cache/<world>/<character>/profile.yaml
```

Examples:

```text
character_cache/Chaimsphere/オド/profile.yaml
character_cache/Chaimsphere/レシュ_成長後/profile.yaml
```
