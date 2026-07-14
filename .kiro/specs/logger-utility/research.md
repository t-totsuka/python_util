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

---

# Gap Analysis: 日次ログローテーション（Issue #7 / Requirement 6, 7）

## Summary
- **Feature**: `logger-utility` への日次ログローテーション追加（ブラウンフィールド拡張）
- **Analysis Date**: 2026-07-14
- **Key Findings**:
  - 既存の `logging` サブパッケージは config_loader / factory / handlers / types の4モジュール構成で、拡張ポイントが明確。ローテーションは `build_file_handler` の差し替えと設定スキーマ拡張で実現できる
  - 標準ライブラリ `logging.handlers.TimedRotatingFileHandler` が日次ローテーション・保持世代管理・書き込み時ロールオーバーを提供し、tech.md の「標準ライブラリ中心」方針と合致する
  - 最大のギャップはファイル名規則: 要件の `{ログの名前}-{日付}.log` は標準の `{ログの名前}.log.YYYY-MM-DD` と異なるため `namer` のカスタマイズが必要で、`namer` を変えると `getFilesToDelete()` による古いファイルの削除判定が壊れる既知の落とし穴がある（サブクラスで両方をオーバーライドするのが安全）

## Current State Investigation

### 既存アセット（src/python_util/logging/）
| ファイル | 役割 | ローテーション対応での関与 |
|---|---|---|
| `types.py` (28行) | `LoggingConfig` / `LoggerOverride`（frozen dataclass） | 拡張: `rotation_enabled`・`retention_days` フィールド追加 |
| `config_loader.py` (100行) | pyproject.toml の `[tool.python_util.logging]` 解析、`_InvalidLoggingConfig` + `warnings.warn` によるフォールバック | 拡張: ローテーション設定キーの解析・検証を追加 |
| `handlers.py` (31行) | `build_console_handler` / `build_file_handler`（現在は `logging.FileHandler` 固定） | 変更の中心: ローテーション対応ハンドラの構築に差し替え |
| `factory.py` (78行) | `get_logger` レジストリ・設定キャッシュ・`_reset_registry` | ほぼ変更不要: `build_file_handler` の引数追加のみ。ロガー個別ファイル（Req 6.7）も同じビルダー経由で自動的に対応される |

### 既存の規約・パターン
- 設定エラーは `_InvalidLoggingConfig` を投げ、`load_config` が `warnings.warn` して**設定全体を** `LoggingConfig()` デフォルトにフォールバック（Req 3.5 の実装パターン）
- テストは `tests/logging/` にモジュール単位でミラーリング（config_loader / factory / handlers / fallback / integration）。`_reset_registry` でグローバル状態をリセット
- ファイルハンドラは UTF-8 固定・追記モード・`%(asctime)s %(levelname)s %(name)s %(message)s` フォーマット

## Requirements Feasibility Analysis

### Requirement-to-Asset Map
| 要件 | 対応アセット | ギャップ種別 |
|---|---|---|
| 6.1 既定で有効 | `types.LoggingConfig` | **Missing**: フィールド追加（default `True`） |
| 6.2 当日ログは設定ファイルへ | `TimedRotatingFileHandler` の baseFilename 動作 | 標準機能で充足 |
| 6.3 日付変更後の最初の書き込みでローテーション | `TimedRotatingFileHandler(when="midnight")` は emit 時にロールオーバー判定。既存ファイルがある場合は mtime 基準で初期ロールオーバー時刻を計算するため、プロセス再起動をまたいでも前日分は退避される | **Unknown**: 再起動をまたぐケースの正確な挙動は設計時に検証（Research Needed） |
| 6.4 `{名前}-{日付}.log` 形式 | 標準は `{名前}.log.YYYY-MM-DD`（末尾サフィックス） | **Missing**: カスタム `namer` が必要 |
| 6.5–6.6 保持期間超過分の削除・既定7日 | `backupCount` + `getFilesToDelete()` | **Constraint**: `getFilesToDelete()` は標準命名（`basename.` プレフィックス）を前提にマッチするため、カスタム `namer` と併用すると削除が機能しない既知の落とし穴。サブクラスで `getFilesToDelete()` もオーバーライドする必要が濃厚（Research Needed: Python 3.11+ での正確な挙動） |
| 6.7 ロガー個別ファイルにも適用 | `factory._configure_logger` → `build_file_handler` | ビルダー差し替えのみで充足 |
| 7.1–7.2 有効/無効・保持日数の設定 | `config_loader._parse_logging_table` | **Missing**: 設定キー追加（キー命名は設計判断: フラット `rotation_enabled`/`retention_days` vs ネスト `[….logging.rotation]`） |
| 7.3 不正値のフォールバック | `_InvalidLoggingConfig` パターン | 既存パターンで充足。ただし現行は「設定全体フォールバック」であり、要件の「既定のローテーション設定にフォールバック」との粒度整合は設計で明確化 |

### 複雑性シグナル
- 時刻駆動の挙動（日付変更）を含むため、**決定的なテスト戦略**が必要（`time.time` のモック、`rolloverAt` の直接操作、`doRollover()` の明示呼び出しなど）
- 「保持期間7日」の解釈: `backupCount=7`（ファイル数ベース。実行しない日があると7日より長く残る）vs 日付パースによる経過日数ベース削除。要件文言は日数だが、日次ローテーション前提ではファイル数ベースが事実上等価。設計で決定
- 既定有効化により**既存利用箇所の挙動が変わる**（ユーザー承認済みの意図的な変更。README への明記が必要）

## Implementation Approach Options

### Option A: 既存モジュール拡張（handlers.py にサブクラスを追加）
- `handlers.py` に `TimedRotatingFileHandler` のサブクラス（`namer` 相当 + `getFilesToDelete` オーバーライド、約30–40行）を定義し、`build_file_handler` を差し替え。`types.py`・`config_loader.py` にフィールド/解析を追加
- ✅ 変更ファイル最小（3ファイル+テスト）、既存の小規模モジュール構成を維持
- ✅ factory は引数の受け渡しのみで無変更に近い
- ❌ handlers.py の責務が「構築」から「ハンドラ実装」へ広がる（31行→80行程度で許容範囲）

### Option B: 新規モジュール分離（rotation.py 追加）
- ローテーション対応ハンドラのサブクラスを新規 `rotation.py` に置き、`handlers.py` はビルダーとして import する
- ✅ 責務分離が明確、ローテーションロジックを単体テストしやすい
- ✅ 将来のローテーション拡張（サイズベース等、現状 Out of scope）の受け皿になる
- ❌ 40行程度のクラスに1モジュールはやや過剰。ファイル数増

### Option C: 完全自作ハンドラ（BaseRotatingHandler 直接継承）
- 命名・削除・ロールオーバー判定をすべて自前実装
- ✅ 命名規則・削除条件を完全制御でき、標準実装の落とし穴を回避
- ❌ 標準実装が持つエッジケース処理（DST、mtime 基準の再起動対応等）を再発明するリスク。tech.md の軽量実装方針に反する

## Effort & Risk
- **Effort: S（1–3日）** — 既存パターンの延長で変更点が局所的。テスト含め小規模
- **Risk: Medium** — `namer`/`getFilesToDelete` の組み合わせと時刻依存テストに既知の落とし穴があるため。実装自体は標準ライブラリの確立された機能

## Recommendations for Design Phase
- **推奨アプローチ**: Option A（handlers.py 拡張）。既存構成の粒度と一貫し、変更が最小。サブクラスが肥大化する場合のみ Option B へ切り替え
- **設計で決めるべき事項**:
  1. 設定キー命名（フラット vs ネストテーブル）— 既存キー（`file`, `level`, `console.enabled`）との一貫性
  2. 保持期間の削除基準（ファイル数 `backupCount` ベース vs 日付経過ベース）
  3. 不正なローテーション設定値のフォールバック粒度（設定全体 vs ローテーション設定のみ）— 現行 Req 3.5 実装は全体フォールバック
- **Research Needed（設計フェーズへ持ち越し）**:
  1. Python 3.11+ の `TimedRotatingFileHandler.getFilesToDelete()` がカスタム `namer` 使用時に削除対象を正しく特定できるかの検証（できない場合はサブクラスでオーバーライド）
  2. プロセス再起動をまたいだ場合のロールオーバー挙動（既存ファイルの mtime 基準判定）が Req 6.3 を満たすかの検証
  3. 時刻依存テストの決定的な実行方法（`doRollover` 直接呼び出し / rolloverAt 操作 / 時刻モック）
- **リスク（設計で明記すべき制約）**:
  - 複数プロセスから同一ログファイルへ書き込む場合のローテーション競合は標準ハンドラでは保証されない（Out of scope として明記推奨）
  - ローテーション既定有効化は既存利用箇所の観測可能な挙動変更（README/CHANGELOG に明記）

---

# Design Discovery: 日次ログローテーション（設計フェーズ検証・2026-07-14）

## Research Log

### TimedRotatingFileHandler のカスタム namer と削除判定の検証
- **Context**: ギャップ分析の Research Needed 1（カスタム `namer` 使用時に `getFilesToDelete()` が削除対象を特定できるか）
- **Sources Consulted**: CPython 3.11 ブランチ `Lib/logging/handlers.py`（raw.githubusercontent.com）、ローカル Python 3.14.0 の同ファイル、実機検証スクリプト
- **Findings**:
  - Python 3.11・3.14 とも `getFilesToDelete()` は `namer` 対応の分岐を持つ。ファイル名から日付パターン `(?<!\d)\d{4}-\d{2}-\d{2}(?!\d)`（アンカーなし）を `search` で探し、`namer(baseFilename + "." + 日付)` の結果と突き合わせて退避ファイルを特定する
  - 実機検証: `app-2026-07-01.log`〜`app-2026-07-09.log` の9ファイル + `backupCount=7` で、最古の2ファイルが正しく削除対象になった。`rolloverAt` を過去に設定して強制ロールオーバーした結果、当日ファイルが `app-2026-07-13.log` へ退避され、保持数7が維持された
  - `namer` はハンドラの属性への関数代入で済み、**サブクラス化は不要**
- **Implications**: ギャップ分析で懸念した「namer と削除判定の非互換」は requires-python `>=3.11` では発生しない。標準ハンドラ + namer 関数のみで Req 6.4/6.5 を実現できる

### プロセス再起動をまたぐロールオーバー（Research Needed 2）
- **Findings**: `TimedRotatingFileHandler.__init__` は既存ログファイルがあればその `st_mtime` を基点に `rolloverAt` を計算する。前日以前の mtime を持つファイルが残っていれば `rolloverAt` は過去となり、再起動後の最初の emit で即ロールオーバーが発火する。退避ファイル名の日付は `rolloverAt - interval`（＝退避対象ログの日付）から生成される
- **Implications**: Req 6.3（日付変更後の最初の書き込みで退避）・6.4（退避対象ログの日付を使用）は再起動をまたぐケースを含め標準実装で充足される

### 時刻依存テストの決定的な実行方法（Research Needed 3）
- **Findings**: `handler.rolloverAt` を過去の時刻に直接設定してから emit することで、時刻モックなしに決定的にロールオーバーを発火できる（実機検証で確認済み）
- **Implications**: テストは `rolloverAt` 操作 + 退避ファイルの事前配置で網羅できる。`time.time` のモックは不要

## Design Decisions

### Decision: 標準 TimedRotatingFileHandler + namer 関数を採用（サブクラス・自作ハンドラは不採用）
- **Alternatives Considered**:
  1. サブクラスで `namer`/`getFilesToDelete` をオーバーライド — 3.11+ では不要と判明
  2. `BaseRotatingHandler` から自作 — DST・mtime 基準再開などの再発明リスク
- **Selected Approach**: `TimedRotatingFileHandler(when="midnight", backupCount=保持日数, encoding="utf-8")` に、モジュールレベルの `namer` 関数（`{stem}.log.YYYY-MM-DD` → `{stem}-YYYY-MM-DD.log`）を代入する
- **Rationale**: 検証により標準実装で全要件を満たせることを確認。tech.md の標準ライブラリ中心・軽量実装方針に最も合致
- **Trade-offs**: ローテーションは emit 契機で発火するため、書き込みが全くない日はファイルが生成されない（日付の抜けが起こり得る）。要件上は問題なし

### Decision: 設定キーはネストテーブル [tool.python_util.logging.rotation] とする
- **Alternatives Considered**: フラットキー（`rotation_enabled`, `retention_days`）
- **Selected Approach**: `rotation.enabled`（bool、既定 `true`）、`rotation.retention_days`（正の整数、既定 `7`）
- **Rationale**: 既存の `console.enabled`/`console.level` と同じネストパターンで、スキーマの一貫性を保つ
- **Trade-offs**: なし（既存キーとの衝突もない）

### Decision: 保持期間はファイル数ベース（backupCount = retention_days）とする
- **Context**: 「保存期間7日間」の解釈（ファイル数 vs 経過日数）
- **Selected Approach**: `backupCount=retention_days` により退避ファイルを最新 N 個保持する
- **Rationale**: 日次ローテーションでは毎日書き込みがあればファイル数＝日数と等価。標準実装をそのまま使え、実装・テストが単純
- **Trade-offs**: 書き込みのない日があると、実カレンダー日数では設定日数より長く残る（許容。design.md に明記）

### Decision: ローテーション設定の不正値は既存パターン踏襲で設定全体フォールバック
- **Context**: Req 7.3 のフォールバック粒度（設定全体 vs ローテーション設定のみ）
- **Selected Approach**: 既存の `_InvalidLoggingConfig` → `warnings.warn` → `LoggingConfig()` 全体フォールバックを踏襲
- **Rationale**: Req 3.5 の実装と同一の観測可能な挙動に統一。フォールバック後の `LoggingConfig()` は既定でローテーション有効・7日保持のため Req 7.3 の文言も充足する

## Synthesis Outcomes
- **Generalization**: ローテーション設定は `LoggingConfig` のフィールド追加として一般化し、ハンドラ構築インターフェース（`build_file_handler`）の引数拡張のみで全ファイルハンドラ（グローバル・ロガー個別）に適用される。Req 6.7 は追加実装なしで充足
- **Build vs Adopt**: Adopt（標準 `TimedRotatingFileHandler`）。自作・サブクラスは検証により不要と判断
- **Simplification**: ギャップ分析 Option A をさらに単純化（サブクラス削除）。新規モジュール・新規コンポーネントは追加せず、既存4モジュールのフィールド/引数/構築ロジック拡張のみで実現

## Risks & Mitigations（追加）
- ローテーション既定有効化は既存利用箇所の観測可能な挙動変更（退避ファイル生成・8日以上前のログ削除）— README/CHANGELOG への明記をタスク化する
- 複数プロセスが同一ログファイルへ書き込む場合のロールオーバー競合は標準ハンドラでは保証されない — Out of Boundary として design.md に明記
- 保持期間はファイル数ベースのため、書き込みがない日を挟むとカレンダー日数で設定値より長く残る — design.md の設定スキーマ説明に明記

## References（追加）
- [logging.handlers — TimedRotatingFileHandler](https://docs.python.org/3/library/logging.handlers.html#timedrotatingfilehandler) — when/backupCount/namer の仕様
- CPython 3.11 `Lib/logging/handlers.py` — `getFilesToDelete()` の namer 対応実装（3.11 で確認）

### 同一ファイルへの複数ハンドラインスタンスとローテーションの競合（設計レビューで検出・2026-07-14）
- **Context**: 設計レビュー（/kiro-validate-design）の Critical Issue 1。単一ファイル統合構成（要件4.1）ではロガー名ごとにファイルハンドラを生成する現行方式だと同一パスに複数の `TimedRotatingFileHandler` が載る
- **Sources Consulted**: 実機検証スクリプト（同一パスに2ハンドラを構築し `rolloverAt` を過去に設定して日付変更を模擬）
- **Findings**: 最初のハンドラがローテーション（リネーム）した後、2つ目のハンドラの `doRollover` は「退避先が既に存在する」ため早期リターンし、ストリームの再オープンも `rolloverAt` の更新も行われない。結果、**2つ目のハンドラの当日ログは退避済みファイル（前日分）へ書き込まれ続ける**（検証結果: `day2 from mod_b` が `app.log.2026-07-13` に混入）
- **Implications**: 設計に「解決済み出力パスをキーとするハンドラキャッシュ（1パス＝1ハンドラインスタンス、全ロガーで共有）」を追加した。`_reset_registry` はこのキャッシュも破棄する。namer の日付抽出も「デフォルト名の末尾サフィックス（最後のドット以降）」と明確化した（設定ファイル名自体に日付を含むケースの誤抽出防止）
