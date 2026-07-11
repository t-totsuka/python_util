# Research & Design Decisions

## Summary
- **Feature**: `progress-display`
- **Discovery Scope**: Extension（既存の `logging` サブパッケージが確立したパターンを踏襲する拡張）
- **Key Findings**:
  - `rich.progress.Progress` は `add_task` / `update` / `remove_task` / `track` / `start` / `stop` を備え、単一インスタンスで複数タスクを同時管理・表示できる。タスク識別子は `TaskID`（int の NewType）で、`add_task` が一意に発行する
  - `Task.finished` プロパティにより現在値が総量に到達したかを判定できるため、完了検知を独自実装する必要はない
  - 既存の `logging` サブパッケージが `pyproject.toml` 設定読み込み・例外命名の canonical パターンを既に確立しており、`progress_display` はこれをそのまま踏襲すべき

## Research Log

### rich.progress.Progress の公開API調査
- **Context**: 複数プログレスの管理・表示APIをどう設計するか判断するため、ラップ対象となる `rich.progress.Progress` の実際のシグネチャを確認する必要があった
- **Sources Consulted**: プロジェクトの `.venv` にインストール済みの `rich` パッケージを `inspect` モジュールで直接調査（`Progress.__init__`, `add_task`, `update`, `remove_task`, `start`, `stop`, `track`, `start_task`, `stop_task`, `Task` の属性一覧）
- **Findings**:
  - `Progress.__init__(*columns, console=None, auto_refresh=True, refresh_per_second=10, transient=False, ...)`
  - `add_task(description: str, start: bool = True, total: float | None = 100.0, completed: int = 0, visible: bool = True, **fields) -> TaskID`
  - `update(task_id: TaskID, *, total=None, completed=None, advance=None, description=None, visible=None, refresh=False, **fields) -> None`
  - `remove_task(task_id: TaskID) -> None`
  - `track(sequence: Iterable, total=None, completed=0, task_id=None, description="Working...", update_period=0.1) -> Iterable`
  - `Task` は `finished`, `percentage`, `started`, `visible` などの読み取り専用プロパティを持つ
- **Implications**: `ProgressDisplay` は独自のタスク管理台帳を持つのではなく、`rich.progress.Progress` インスタンスと `TaskID` をそのまま利用する薄いラッパーとして設計できる。完了判定は `Task.finished` を都度参照すればよく、独自の完了検知ロジックは不要

### 既存 `logging` サブパッケージの規約調査
- **Context**: `tech.md` に明記された「サブパッケージ固有の設定は呼び出し側 `pyproject.toml` の `[tool.python_util.<name>]` テーブルから読み込む」パターンの実装詳細を確認するため、`src/python_util/logging/config_loader.py` を精査した
- **Sources Consulted**: `src/python_util/logging/config_loader.py`, `src/python_util/logging/types.py`, `src/python_util/logging/__init__.py`
- **Findings**:
  - 設定読み込みは `load_config(start_dir: Path | None) -> XxxConfig` という関数で、呼び出し側ディレクトリから親方向に `pyproject.toml` を探索する
  - テーブルが存在しない場合・TOML解析に失敗した場合は例外を送出せず `warnings.warn` で警告しデフォルト値にフォールバックする
  - テーブル固有の値検証失敗は非公開の内部例外（例: `_InvalidLoggingConfig`、先頭アンダースコア）で表現し、`load_config` 内で捕捉して警告に変換する。一方、呼び出し側が実行時に遭遇しうる値エラー（例: `time_utility.exceptions.InvalidTimezoneError`）は非公開にせず `exceptions.py` に公開クラスとして定義する
  - 公開APIは `__init__.py` の `__all__` に限定し、内部モジュールへの直接importを利用側にさせない
- **Implications**: `progress_display` は `config_loader.py`（`_InvalidProgressDisplayConfig` という内部例外を使う）と `exceptions.py`（`UnknownTaskError` 等の公開例外）を分離し、`logging` と同一の探索・フォールバック挙動を再実装する

## Architecture Pattern Evaluation

| Option | Description | Strengths | Risks / Limitations | Notes |
|--------|-------------|-----------|---------------------|-------|
| 薄いラッパー（採用） | `rich.progress.Progress` を1インスタンスだけ内部に保持し、`TaskID` をそのまま公開する最小限のファサード | 実装量が少なく `rich` の全機能（列カスタマイズ・スピナー等）をそのまま利用可能。`logging` サブパッケージの「stdlib/既存ライブラリをそのまま返す」思想と一貫 | `rich.progress.Progress` の将来的なAPI変更の影響を直接受ける | 個人用ユーティリティ集としての薄さ・保守容易性を優先する `tech.md` の方針に合致 |
| 独自タスクモデルの二重管理 | `ProgressDisplay` が独自の `TaskRecord` 台帳を持ち、`rich` とは別に状態を保持する | `rich` への依存を抽象化できる | 状態同期のバグリスク、実装量増、要件が求める以上の抽象化 | YAGNI に反するため不採用 |

## Design Decisions

### Decision: タスク識別子は `rich.progress.TaskID` をそのまま公開する
- **Context**: Requirement 1.1 は「一意なタスク識別子の発行」を求めているが、独自型を新設するか `rich` の型を再利用するかの判断が必要だった
- **Alternatives Considered**:
  1. 独自の `TaskId`（`NewType`）を定義し、内部で `rich.progress.TaskID` とマッピングする
  2. `rich.progress.TaskID` をそのまま公開APIの戻り値・引数型として再利用する
- **Selected Approach**: 選択肢2。`ProgressDisplay.add_task()` の戻り値、`update()`/`remove_task()` の引数型として `rich.progress.TaskID` を直接使用する
- **Rationale**: `logging` サブパッケージが `get_logger()` で stdlib の `logging.Logger` をそのまま返している既存パターンと一貫する。マッピング層を追加しても要件上の利益がない
- **Trade-offs**: `rich` への直接依存が公開APIの型シグネチャに漏れるが、`tech.md` は既に `rich` をコア技術として採用しており許容範囲
- **Follow-up**: なし

### Decision: 完了判定・自動非表示はイベント駆動ではなく `update()` 呼び出し時の同期チェックで行う
- **Context**: Requirement 3.3（完了状態への遷移）と 3.6（完了タスクの自動非表示）をどう実装するか
- **Alternatives Considered**:
  1. バックグラウンドスレッド/タイマーで定期的に全タスクの完了を監視する
  2. `update()` 呼び出しの都度、更新対象タスクの `Task.finished` を同期的に確認し、設定が有効なら即座に `remove_task` する
- **Selected Approach**: 選択肢2
- **Rationale**: `rich.progress.Progress` は単一スレッドでの同期的な使用を前提としており、バックグラウンド監視はスコープ外（Boundary Context の Out of scope: マルチスレッド間の進捗集約）と矛盾する。同期チェックは実装が単純で `rich` のレンダリングループ（`auto_refresh`）とも競合しない
- **Trade-offs**: `update()` が呼ばれない限り完了検知・自動非表示は発生しない（ポーリングではないため、利用者が最後に `advance`/`completed` を反映する呼び出しを行う必要がある）
- **Follow-up**: 実装時に、`add_task` 時点で `completed >= total` となるケースも同様に即時判定することを確認する

### Decision: 設定テーブル名・フォールバック規約は `logging` と完全に揃える
- **Context**: Requirement 4 は `[tool.python_util.progress_display]` からの設定読み込みを求めている
- **Alternatives Considered**:
  1. `progress_display` 独自の設定ファイル形式・探索ロジックを新設する
  2. `logging/config_loader.py` と同一の探索アルゴリズム（`pyproject.toml` を親ディレクトリ方向に探索）・フォールバック規約（`warnings.warn` + デフォルト値）を再利用する
- **Selected Approach**: 選択肢2
- **Rationale**: `structure.md`/`tech.md` が明記する確立済みパターンであり、一貫性と学習コストの低さを優先する
- **Trade-offs**: `config_loader.py` のロジックが `logging` と `progress_display` の2箇所に重複するが、共通化はサブパッケージ間の結合を生むため現時点では見送る（既存構成でも共通化されていない）
- **Follow-up**: なし

## Risks & Mitigations
- `rich.progress.Progress` はマルチスレッドからの同時更新を安全に扱う保証がない — Boundary Context で明示的にスコープ外とし、シングルスレッド利用を前提とする
- 完了タスクの自動非表示を有効にした状態で高頻度に `add_task`/`update` を行うと表示のちらつきが起こり得る — デフォルトは無効（`auto_remove_finished: false`）とし、利用者の明示的なオプトインを必須にする
- `config_loader.py` のロジック重複（`logging` と `progress_display`）が将来の仕様変更時に同期漏れを起こす可能性 — 将来複数サブパッケージ目の重複が生じた時点で共通化を再検討する

## References
- `src/python_util/logging/config_loader.py` — pyproject.toml 探索・フォールバックの既存実装
- `src/python_util/time_utility/exceptions.py` — 公開例外の命名規約の既存実装
- `.venv/lib/python3.14/site-packages/rich/progress.py` — `rich.progress.Progress` の実装（`inspect` によるシグネチャ確認元）
