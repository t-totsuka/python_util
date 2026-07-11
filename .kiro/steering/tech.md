# 技術スタック

## アーキテクチャ

単一の Python パッケージとして構成し、機能ごとにモジュールを分割するシンプルな構成を想定。

## コア技術

- **言語**: Python（標準ライブラリ中心。外部依存は必要最小限に留める）
- **パッケージ管理**: pdm（`pyproject.toml` ベース）
- **ロギング/コンソール出力**: rich

## 主要ライブラリ

- `rich`: ロギングやコンソール出力の整形に使用

## 開発標準

### 型安全性・コード品質・テスト

- 型ヒントを必須とし、全モジュール冒頭で `from __future__ import annotations` を宣言する
- 不正な型・値は早期に検出し、`TypeError`（型不正）または専用の例外クラス（値不正）を送出する
- サブパッケージ固有の例外は `exceptions.py` に集約し、`ValueError` を継承する（例: `time_utility.exceptions.InvalidTimezoneError`）。パッケージ内部限定の失敗は公開しない内部例外として先頭アンダースコアを付ける（例: `logging.config_loader._InvalidLoggingConfig`）
- 公開関数には日本語の一行docstringを付け、モジュール冒頭にもモジュールの役割を一行docstringで記す
- テストは pytest。`tests/` は `src/python_util/` の構成をミラーリングし、各ディレクトリに `__init__.py` を置く
- lint/型チェッカーはruffを導入する

## 開発環境

### 必須ツール
- Python（バージョンは `pyproject.toml` の `requires-python` に準拠）
- pdm

### よく使うコマンド
```bash
# 依存関係インストール: pdm install
# 実行例: pdm run python -m <module>
```

## 主要な技術的決定

- 標準ライブラリを優先し、外部依存は最小限に留める
- ロギング/コンソール出力には rich を採用
- パッケージ管理は pdm（`pyproject.toml`）に統一
- サブパッケージ固有の設定は、呼び出し側 `pyproject.toml` の `[tool.python_util.<subpackage>]` テーブルから読み込む（`logging` で採用済みのパターン。設定ファイルの解析失敗時はコードを止めず `warnings.warn` で警告してデフォルト値にフォールバックする）
- タイムゾーンを扱うユーティリティ（`time_utility`）は JST を既定値とする

---
_2026-07-11: `logging`, `time_utility` の実装を踏まえて同期。開発標準セクションを実コードのパターンで更新。_
