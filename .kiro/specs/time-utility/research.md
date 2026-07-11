# Research & Design Decisions

## Summary
- **Feature**: `time-utility`
- **Discovery Scope**: Simple Addition(標準ライブラリのみで完結する新規ユーティリティモジュール)
- **Key Findings**:
  - Python 3.11+(本プロジェクトの `requires-python`)では `zoneinfo` が標準ライブラリに含まれ、`ZoneInfo("Asia/Tokyo")` で追加パッケージなしにJSTを扱える
  - WindowsはOSにIANAタイムゾーンDBを同梱しないため `zoneinfo` が `ZoneInfoNotFoundError` を送出しうる。本プロジェクトはWindows環境での利用も行うため、`tzdata` パッケージを `sys_platform == "win32"` 限定の条件付き必須依存として追加する
  - 既存の `python_util.logging` パッケージが「機能単位でモジュール分割 + `__init__.py` で公開APIを絞る」という一貫したパターンを持っており、`time_utility` もこれに追従するのが自然

## Research Log

### zoneinfoとtzdataの必要性
- **Context**: 「標準モジュールだとロケール設定が煩雑」という要件があり、外部依存を増やさずJSTを扱えるか確認する必要があった
- **Sources Consulted**: Python公式ドキュメント(`zoneinfo` — IANA time zone support)、`tzdata` PyPIパッケージの説明
- **Findings**:
  - `zoneinfo` はPython 3.9+の標準ライブラリで、Linux/macOSは通常OSに同梱されたIANAタイムゾーンDBを利用できる
  - Windowsおよび最小構成のコンテナ環境ではOSにタイムゾーンDBが存在しない場合があり、`zoneinfo.ZoneInfoNotFoundError` が発生し得る
  - `tzdata` パッケージ(純Pythonのデータパッケージ)をインストールすると、OSのDBが無い場合のフォールバックとして `zoneinfo` が自動的に利用する
- **Implications**: 本体の実装は標準ライブラリの `zoneinfo` のみに依存する。可搬性を高めるため `pyproject.toml` に `tzdata` を `sys_platform == "win32"` 限定の依存として追加することを設計に含める(必須ではないが低コストな保険)

### 日本語の曜日・日付表記とlocale回避
- **Context**: 「ロケール設定が煩雑」を解消し、`locale.setlocale` なしで日本語表記(曜日等)を生成する方法を確認する必要があった
- **Sources Consulted**: Python公式ドキュメント(`datetime.strftime`, `locale` モジュールの注意点)
- **Findings**:
  - `strftime("%a")` 等はプロセスのグローバルロケール設定に依存し、`locale.setlocale` はスレッドセーフではなくアプリ全体に影響するため好ましくない
  - ロケールに依存せず日本語の曜日名を得るには、`datetime.weekday()` の整数値から固定の日本語曜日名テーブル(月,火,水,木,金,土,日)を引く方式が確実かつスレッドセーフ
- **Implications**: フォーマット機能は `locale` モジュールを一切使用せず、固定テーブルによる曜日名解決とテンプレート文字列の組み立てで日本語表記を実現する

### 既存パッケージ構成パターンの確認
- **Context**: `src/python_util/` 配下に新規モジュールを追加するにあたり、既存の `logging` パッケージの構成規約を踏襲できるか確認した
- **Sources Consulted**: `src/python_util/logging/__init__.py`, `factory.py`, `types.py`(リポジトリ内コード)
- **Findings**:
  - `logging` パッケージは `types.py`(値オブジェクト/dataclass)、機能別モジュール(`factory.py`, `handlers.py`, `config_loader.py`)、`__init__.py` で公開APIのみを再エクスポートする構成
  - 公開APIは関数ベース(`get_logger`)であり、クラスベースのAPIではない。`frozen dataclass` は設定値オブジェクトとして使われている
- **Implications**: `time_utility` も同様に関数ベースの公開API + `frozen dataclass`/`Enum` による値オブジェクトという構成に統一する。要件文書の「utilityクラス」という表現は機能領域を指す言葉として解釈し、実装はプロジェクト規約に合わせて関数群として設計する

## Architecture Pattern Evaluation

| Option | Description | Strengths | Risks / Limitations | Notes |
|--------|-------------|-----------|---------------------|-------|
| 関数ベースのモジュール群(採用) | `clock`/`convert`/`formatting` 等の機能別モジュールと `__init__.py` での公開API集約 | 既存 `logging` パッケージと一貫性、テストしやすい、状態を持たずスレッドセーフ | モジュール数がやや増える | `python_util.logging` と同一パターン |
| 単一 `TimeUtility` クラス | すべての操作をクラスメソッド/インスタンスメソッドとして提供 | 要件文書の字面に忠実 | 既存コードベースの関数ベース規約と不整合、状態を持たない処理にクラスは不要な複雑さを追加 | 不採用 |

## Design Decisions

### Decision: 公開APIを関数ベースのモジュール群として設計する
- **Context**: 要件文書では「utilityクラス」と表現されているが、実装スタイルを決める必要がある
- **Alternatives Considered**:
  1. 単一のクラス(`TimeUtility`)にすべてのメソッドを持たせる
  2. 機能別モジュール + 関数群 + `__init__.py` での公開API集約(既存 `logging` パッケージと同型)
- **Selected Approach**: 機能別モジュール(`clock.py`, `convert.py`, `formatting.py`, `timezones.py`, `exceptions.py`)に処理を分割し、`__init__.py` で公開関数のみを再エクスポートする
- **Rationale**: 状態を持たない時刻操作にクラスは不要であり、既存の `logging` パッケージとの一貫性を保つ方がプロジェクト全体の保守性が高い
- **Trade-offs**: 要件文書の字面(クラス)とは異なる実装形態になるが、機能的な要求(JSTデフォルト・変換・フォーマット・エラー処理)は全て満たされる
- **Follow-up**: 実装時に `__init__.py` の公開シンボル一覧を要件のAcceptance Criteriaと突き合わせて漏れがないか確認する

### Decision: JSTの解決を `zoneinfo.ZoneInfo("Asia/Tokyo")` に一本化する
- **Context**: JSTをデフォルトタイムゾーンとして扱うにあたり、固定オフセット(`timezone(timedelta(hours=9))`)か `zoneinfo` かを選ぶ必要があった
- **Alternatives Considered**:
  1. `datetime.timezone(timedelta(hours=9))` による固定オフセット
  2. `zoneinfo.ZoneInfo("Asia/Tokyo")` によるIANAタイムゾーン
- **Selected Approach**: `zoneinfo.ZoneInfo("Asia/Tokyo")` を使用する
- **Rationale**: 日本は夏時間を採用していないため実用上の差はほぼ無いが、`zoneinfo` を使うことで他タイムゾーンとの変換APIを統一的に扱え、将来的な拡張(他タイムゾーン対応)にも自然に接続できる
- **Trade-offs**: 環境によっては `tzdata` パッケージの追加が必要になる場合がある(上記Research Log参照)
- **Follow-up**: Windows環境での動作確認を実施する。`pyproject.toml` への `tzdata`(`sys_platform == "win32"` 限定)追加はタスク化して実装時に対応する

## Risks & Mitigations
- Windows環境でOSにタイムゾーンDBが存在せず `zoneinfo.ZoneInfoNotFoundError` が発生するリスク — 本プロジェクトはWindowsでの利用を予定しているため、`tzdata` を `sys_platform == "win32"` 限定の条件付き必須依存として `pyproject.toml` に追加して緩和する
- タイムゾーン名の入力ミス(例: "Asia/Tokio" などのtypo)によるランタイムエラー — `resolve_timezone` で `ZoneInfoNotFoundError` を捕捉し、要件5.1に定義された `InvalidTimezoneError` として送出し直すことで明確なエラーメッセージを保証する
- naiveなdatetimeを誤ってUTC扱いしてしまう既存datetimeライブラリの一般的な落とし穴 — `ensure_aware` を全ての変換・フォーマット関数のエントリポイントで一貫して適用し、naiveな入力は常にJSTとして解釈する規約を徹底する

## References
- [zoneinfo — IANA time zone support](https://docs.python.org/3/library/zoneinfo.html) — 標準ライブラリでのタイムゾーン解決とtzdataフォールバックの挙動
- [tzdata (PyPI)](https://pypi.org/project/tzdata/) — OSにタイムゾーンDBが無い環境向けの純Pythonデータパッケージ
