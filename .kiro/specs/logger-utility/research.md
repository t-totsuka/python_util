# Research & Design Decisions Template

## Summary
- **Feature**: `logger-utility`
- **Discovery Scope**: New Feature（グリーンフィールド、既存コードなし。ただしスコープは小〜中規模のラッパーユーティリティ）
- **Key Findings**:
  - `rich.logging.RichHandler` は `logging` モジュールの標準ハンドラとして差し込み可能で、コンソール向け整形出力に適する一方、ファイル出力にはANSI装飾のない`logging.FileHandler`（プレーンフォーマッタ）を使うのが一般的パターン
  - Python標準の`tomllib`（3.11+で標準搭載）を使えば外部依存を増やさずに`pyproject.toml`を解析できる。`[tool.<name>]`テーブルはサードパーティツール専用に予約されている
  - ロガーの重複ハンドラ登録は`logging`モジュールの典型的な落とし穴であり、モジュールレベルのレジストリで「設定済みロガー名」を追跡して防ぐ設計が定石

## Research Log

### RichHandlerによるコンソール出力
- **Context**: 要件1.3で`rich`を用いた整形出力が求められている
- **Sources Consulted**: [Logging Handler — Rich 14.1.0 documentation](https://rich.readthedocs.io/en/latest/logging.html), [Use Rich Loghandler in combination with other handlers · Textualize/rich · Discussion #1582](https://github.com/Textualize/rich/discussions/1582), [Python logging with rich - writing to stderr - plain output when writing to file](https://robinbowes.blogspot.com/2025/02/python-logging-with-rich-writing-to.html)
- **Findings**:
  - `RichHandler`は`logging.Handler`のサブクラスであり、他の標準ハンドラ（`FileHandler`）と`Logger.addHandler()`で共存できる
  - コンソール用フォーマッタは`"%(message)s"`のみとし、時刻・レベル・ファイル位置の装飾は`RichHandler`自身に任せるのが推奨パターン
  - ファイル出力にRichの装飾（ANSIエスケープ）をそのまま書き込むと可読性を損なうため、ファイル用ハンドラには別のプレーンな`Formatter`（時刻・レベル・ロガー名・メッセージ）を使う
- **Implications**: コンソール用ハンドラとファイル用ハンドラを分離して構築し、それぞれに適したフォーマッタを割り当てる設計とする

### pyproject.tomlからの設定読み込み
- **Context**: 要件3で呼び出し側の`pyproject.toml`から設定を読み込む必要がある
- **Sources Consulted**: [tomllib — Parse TOML files](https://docs.python.org/3/library/tomllib.html), [Python and TOML: Read, Write, and Configure with tomllib – Real Python](https://realpython.com/python-toml/), [Writing your pyproject.toml - Python Packaging User Guide](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/)
- **Findings**:
  - `tomllib`は標準ライブラリ（Python 3.11以降）であり、追加の外部依存を必要としない。読み込みはバイナリモード（`"rb"`）必須
  - `pyproject.toml`の`[tool.<name>]`テーブルはサードパーティツール専用の名前空間として予約されており、本ライブラリは`[tool.python_util.logging]`を使用するのが規約に沿う
  - ライブラリが呼び出し側の`pyproject.toml`を発見する標準的な方法は、カレントワーキングディレクトリから親ディレクトリへ`pyproject.toml`が見つかるまで遡る探索（black・ruff等の設定探索と同様のパターン）
- **Implications**: `tomllib`を採用し、`requires-python`は`>=3.11`とする。設定探索はカレントディレクトリ基点の上方探索とし、シンボリックリンクやモノレポでの複雑な探索は本スペックのスコープ外とする

### 重複ハンドラ登録の防止
- **Context**: 要件4.3で同一ロガーへのハンドラ重複登録を禁止している
- **Sources Consulted**: [rich.logging — Rich 14.1.0 documentation](https://rich.readthedocs.io/en/stable/reference/logging.html)、Python標準`logging`モジュールの一般的な既知の落とし穴（`getLogger`は同名なら同一インスタンスを返すが、呼び出しの都度`addHandler`すると重複する）
- **Findings**:
  - `logging.getLogger(name)`は同名であれば同一の`Logger`インスタンスを返すため、本ライブラリが独自に「設定済みロガー名」を記録し、初回のみハンドラを追加する制御が必要
  - `Logger.propagate = False`を設定named loggerに直接ハンドラを付ける場合、ルートロガーへの伝播による二重出力も避けられる
- **Implications**: モジュールレベルのレジストリ（設定済みロガー名の集合）を持つファクトリを設計し、初回呼び出し時のみハンドラ構築・登録を行う

## Architecture Pattern Evaluation

| Option | Description | Strengths | Risks / Limitations | Notes |
|--------|-------------|-----------|---------------------|-------|
| Facade + 標準loggingラップ | `get_logger()`ファサードの背後で標準`logging`モジュールを設定し、`RichHandler`/`FileHandler`を注入 | 標準`logging`との完全互換、呼び出し側は`logging.Logger`の全APIをそのまま使える、学習コスト最小 | 標準`logging`のグローバル状態（モジュールレベルのレジストリ）に依存するため、テスト時は明示的なリセットが必要 | 採用。既存steering方針（標準ライブラリ中心・軽量実装）と合致 |
| 独自Loggerクラスによるラッパー | `logging.Logger`を継承・独自クラスでカプセル化 | 独自インターフェースを厳密に制御できる | 標準`logging`と混在利用時に混乱を招く、既存コードとの互換性が下がる | 不採用。過剰設計 |
| Loguru等サードパーティロギングライブラリの導入 | Loguruのように高機能なロギングライブラリを採用 | ローテーション等の高度な機能を標準搭載 | 「外部依存は必要最小限」というproduct.md/tech.mdの方針に反する。richと役割重複 | 不採用 |

## Design Decisions

### Decision: 設定探索はカレントディレクトリ基点の上方探索とする
- **Context**: 呼び出し側は複数ファイル・クラスから構成されるため、ライブラリはどのプロセスからでも呼び出し側の`pyproject.toml`を一意に特定する必要がある
- **Alternatives Considered**:
  1. 呼び出し元スクリプトの`__file__`から遡る — importするモジュールの位置に依存し、パッケージ配置によって挙動がぶれる
  2. カレントワーキングディレクトリ(`Path.cwd()`)から親ディレクトリへ`pyproject.toml`が見つかるまで遡る — black/ruff等のツールと同様の慣習
- **Selected Approach**: カレントワーキングディレクトリ基点の上方探索
- **Rationale**: 呼び出し側は通常プロジェクトルートから実行されるため、既存のPythonツールチェーン（black, ruff, mypy等）と同じ規約に従うことで開発者の期待に合致する
- **Trade-offs**: 呼び出し側が非標準的なディレクトリからプロセスを起動した場合は`pyproject.toml`が見つからずデフォルト設定にフォールバックする（要件3.4でカバー済み）
- **Follow-up**: 実装時にモノレポ構成での探索範囲（`pyproject.toml`が複数存在するケース）を検証する

### Decision: tomllibを採用しrequires-pythonを>=3.11とする
- **Context**: 外部依存を増やさずTOML解析を行いたい（tech.md: 標準ライブラリ中心）
- **Alternatives Considered**:
  1. `tomli`（サードパーティ、3.11未満をサポート） — 外部依存が増える
  2. `tomllib`（標準ライブラリ、3.11以降のみ） — 外部依存なし
- **Selected Approach**: `tomllib`
- **Rationale**: product.md/tech.mdの「外部依存は必要最小限」という方針に最も合致する
- **Trade-offs**: Python 3.10以前のプロジェクトからは利用できない制約が生まれる
- **Follow-up**: `pyproject.toml`の`requires-python`を`>=3.11`に設定することをタスクで明示する

## Risks & Mitigations
- 呼び出し側の`pyproject.toml`が複数階層に存在する（モノレポ）場合に誤った設定を読む可能性 — 上方探索は最初に見つかった`pyproject.toml`を採用し、それ以上は遡らない仕様として明確化する
- ログファイルへの書き込み権限がない環境での失敗 — ディレクトリ作成失敗時はコンソール出力のみにフォールバックし、警告を出す
- 設定スキーマの将来的な拡張時に後方互換性が壊れるリスク — スキーマキーの追加のみで対応し、既存キーの意味変更は行わない方針をRevalidation Triggersに明記

## References
- [Logging Handler — Rich 14.1.0 documentation](https://rich.readthedocs.io/en/latest/logging.html) — RichHandlerの基本設定方法
- [rich.logging — Rich 14.1.0 documentation](https://rich.readthedocs.io/en/stable/reference/logging.html) — RichHandlerのAPIリファレンス
- [tomllib — Parse TOML files](https://docs.python.org/3/library/tomllib.html) — 標準ライブラリによるTOML解析
- [Writing your pyproject.toml - Python Packaging User Guide](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/) — `[tool.*]`テーブルの規約
</content>
