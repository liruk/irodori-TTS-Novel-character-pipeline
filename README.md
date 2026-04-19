# Irodori Character Pipeline

小説本文からキャラクター設定 YAML を作り、実行中の Irodori VoiceDesign サーバーに投げて音声サンプルを一括生成するための共有用リポジトリです。

このリポジトリは、Irodori の学習・推論本体とは切り離して使う前提です。扱う境界は次の 3 つです。

- 小説本文や章ファイル
- 再利用可能な `character_cache`
- 外部で起動している VoiceDesign Gradio サーバー

## できること

- 小説から抽出した設定を `profile.yaml` 形式でそろえる
- その YAML 群を検証する
- `voice_design` 情報を使って VoiceDesign サーバーへバッチ生成をかける
- 生成結果を manifest 付きで保存する

## 構成

- `SKILL.md`
  - Codex から使うための skill 本体
- `references/profile-schema.md`
  - `profile.yaml` の推奨スキーマ
- `references/extraction-guidelines.md`
  - 本文から声や設定を拾うときの判断基準
- `scripts/validate_profiles.py`
  - プロファイル検証スクリプト
- `scripts/generate_voice_samples.py`
  - VoiceDesign サーバー呼び出し用スクリプト

## セットアップ

`uv` を使います。

```bash
uv sync
```

以後の実行も `uv run` 前提です。

## 想定するキャッシュ配置

本文の入力側は、次のような配置を標準とします。

```text
manuscripts/<world>/<arc-or-chapter>/*.md
```

例:

```text
manuscripts/Chaimsphere/chapter1/01.md
manuscripts/Chaimsphere/chapter1/02.md
manuscripts/Chaimsphere/chapter4/01.md
```

既存プロジェクトですでに別の本文配置がある場合は、無理に移動せずそのまま使って構いません。ただし、その場合でも `source` に参照元を残す前提です。

出力側のキャッシュは次の形を想定します。

```text
character_cache/<world>/<character>/profile.yaml
```

例:

```text
character_cache/Chaimsphere/オド/profile.yaml
character_cache/Chaimsphere/レシュ_成長後/profile.yaml
```

音声生成対象の `profile.yaml` には `voice_design` が必要です。

まとめると、基本の対応はこうです。

- 入力: `manuscripts/<world>/...`
- 出力: `character_cache/<world>/<character>/profile.yaml`

## プロファイル検証

```bash
uv run python scripts/validate_profiles.py --character-cache /path/to/character_cache
```

新規追加や項目名変更のあとには、先にこの検証を通す想定です。

## 音声サンプル生成

先に Irodori VoiceDesign の Gradio サーバーを起動しておき、その後で:

```bash
uv run python scripts/generate_voice_samples.py \
  --character-cache /path/to/character_cache \
  --gradio-url http://127.0.0.1:7861/
```

よく使うオプション:

- `--characters オド ソルカ`
- `--limit 1`
- `--output-root generated_character_samples`

## 補足

- 生成音声はキャッシュの外に保存します。
- 新しめの Gradio で `/gradio_api` 配下に API がある構成にも対応しています。
- 本文からの設定抽出そのものは半自動・手動前提で、このリポジトリではスキーマと生成境界を標準化しています。
- 本文の実配置が標準形と違う場合は、その実パスを `source.evidence` などで追跡できるようにしておくと運用しやすいです。
