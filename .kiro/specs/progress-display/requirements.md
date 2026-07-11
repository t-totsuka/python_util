# Requirements Document

## Project Description (Input)

richのprogress displayを拡張して簡単に複数のプログレスを表示できるようにしたい

## Introduction

本機能は、`rich.progress.Progress` をラップし、複数の進捗（プログレス）を単一のコンソール表示領域にまとめて管理・表示できるユーティリティを `python_util` のサブパッケージとして提供する。利用者は最小限のコードで複数タスクの進捗表示を開始・更新・終了でき、他のサブパッケージ（`logging`, `time_utility`）と同様に、呼び出し側 `pyproject.toml` の `[tool.python_util.progress_display]` テーブルを通じて挙動をカスタマイズできる。

## Boundary Context (Optional)

- **In scope**: 複数タスクの進捗を単一の表示領域で管理するAPI、タスクの追加・更新・削除・完了、コンテキストマネージャによる開始/終了、イテラブルに対する進捗表示ヘルパー、`pyproject.toml` 経由の設定オーバーライド、専用例外によるエラー通知
- **Out of scope**: マルチプロセス/マルチスレッド間での進捗集約、ネットワーク経由での進捗配信、進捗履歴の永続化・ログファイルへの記録、`rich.progress.Progress` 自体の再実装
- **Adjacent expectations**: コンソール出力に関する挙動は既存の `logging` サブパッケージと競合しないこと（同一コンソール/ハンドラーを奪い合わない）。設定オーバーライドの仕組みは `logging` サブパッケージで採用されているパターン（`[tool.python_util.<name>]` テーブル、解析失敗時は `warnings.warn` でデフォルトにフォールバック）に準拠する。

## Requirements

### Requirement 1: 複数プログレスタスクの一元管理・表示

**Objective:** As a 開発者（本ライブラリの利用者）, I want 複数の進捗を一つの表示にまとめて管理したい, so that 複数の処理の進行状況を一目で把握できる

#### Acceptance Criteria

1. When 利用者が新しい進捗タスクを追加する, the ProgressDisplay shall 一意なタスク識別子を発行し、そのタスクを管理対象に加える
2. While 複数のタスクが管理されている, the ProgressDisplay shall すべてのタスクの進捗を単一のコンソール表示領域に同時に表示する
3. When いずれかのタスクの進捗値が更新される, the ProgressDisplay shall 対象タスクの表示を即座に反映する
4. The ProgressDisplay shall 各タスクに説明文（ラベル）、現在値、総量を関連付けて表示する
5. If 存在しないタスク識別子に対する操作が要求された, then the ProgressDisplay shall 専用の例外を送出する

### Requirement 2: シンプルなAPIによる表示の開始・終了

**Objective:** As a 開発者, I want 最小限のコードでプログレス表示を開始・終了したい, so that 既存の処理に手軽に進捗表示を組み込める

#### Acceptance Criteria

1. When 利用者がProgressDisplayをコンテキストマネージャとして起動する, the ProgressDisplay shall 表示を開始し、ブロックを抜ける際に表示を自動的に終了する
2. Where イテラブルに対する進捗表示が必要な場合, the ProgressDisplay shall for文でイテレートしながら進捗を自動更新するヘルパーを提供する
3. The ProgressDisplay shall スピナー、進捗バー、パーセンテージ、残り時間の表示など、`rich.progress.Progress` が備える主要な表示要素を利用可能にする
4. While ProgressDisplayが開始されていない状態にある, the ProgressDisplay shall タスクの追加・更新要求に対して専用の例外を送出する

### Requirement 3: タスクのライフサイクル管理

**Objective:** As a 開発者, I want 個々の進捗タスクを追加・更新・削除・完了させたい, so that 動的に増減する処理の進捗を柔軟に扱える

#### Acceptance Criteria

1. When 利用者がタスクを追加する, the ProgressDisplay shall 総量（total）と初期の現在値（completed）を指定可能にする
2. When 利用者が既存タスクの進捗を更新する, the ProgressDisplay shall 現在値の絶対値指定と相対増分（advance）指定の両方をサポートする
3. When タスクの現在値が総量に到達する, the ProgressDisplay shall 当該タスクを完了状態として表示する
4. When 利用者がタスクを明示的に削除する, the ProgressDisplay shall 該当タスクを表示対象から取り除く
5. If 総量に0以下または負の値が指定された, then the ProgressDisplay shall 専用の例外を送出する
6. Where 完了済みタスクの自動非表示が設定で有効化されている, the ProgressDisplay shall 完了したタスクを表示から自動的に取り除く

### Requirement 4: pyproject.toml経由の設定カスタマイズ

**Objective:** As a 開発者, I want 呼び出し側のpyproject.tomlから表示挙動を調整したい, so that コードを変更せずにプロジェクトごとに見た目や動作を変えられる

#### Acceptance Criteria

1. Where 呼び出し側の `pyproject.toml` に `[tool.python_util.progress_display]` テーブルが存在する, the ProgressDisplay shall そのテーブルの設定値を読み込み挙動に反映する
2. The ProgressDisplay shall 完了済みタスクの自動非表示の有効/無効を設定可能にする
3. The ProgressDisplay shall 表示の更新頻度（refresh_rate）を設定可能にする
4. If 設定テーブルの解析に失敗した, then the ProgressDisplay shall `warnings.warn` で警告した上でデフォルト設定にフォールバックする
5. When `pyproject.toml` に `[tool.python_util.progress_display]` テーブルが存在しない, the ProgressDisplay shall デフォルト設定で動作する

### Requirement 5: エラー処理

**Objective:** As a 開発者, I want 不正な操作や不正な値が明確なエラーとして検出されたい, so that 実装時のバグを早期に発見できる

#### Acceptance Criteria

1. If 不正な型の引数が渡された, then the ProgressDisplay shall `TypeError` を送出する
2. If サブパッケージ固有の値エラーが発生した, then the ProgressDisplay shall `exceptions.py` に集約された専用例外（`ValueError` を継承）を送出する
3. The ProgressDisplay shall 例外発生時にも表示領域を破損させず、コンテキストマネージャ終了時に表示を正しくクリーンアップする
