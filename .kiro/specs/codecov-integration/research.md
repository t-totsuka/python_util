# Research & Design Decisions

## Summary
- **Feature**: `codecov-integration`
- **Discovery Scope**: Extension（既存GitHub Actions CI設定の修正・統合）
- **Key Findings**:
  - 既存の2ワークフロー(`ci.yml`, `unit-test.yml`)はいずれも`requirements.txt`不在・`master`ブランチ誤指定・プロジェクト自体の未インストールにより実質的に動作していない可能性が高い
  - `codecov/test-results-action`は非推奨であり、`codecov/codecov-action@v5`を`report-type: test_results`パラメータ付きで2回目に呼び出す方式へ移行することが公式に推奨されている
  - カバレッジしきい値によるCI失敗は、Codecov側の非同期ステータスチェック(`codecov.yml`)に頼るとGitHub側のブランチ保護設定（本リポジトリのコード変更では制御不能な手動設定）に依存してしまうため、`pytest-cov`が既に持つ`--cov-fail-under`オプションをCIジョブ自身の失敗条件として採用する方が、単一リポジトリ内で完結し即時的に検証可能

## Research Log

### 既存ワークフローの動作可否
- **Context**: `ci.yml`/`unit-test.yml`が実際にテストを実行できているか（ユーザーヒアリングで「中途半端」と申告あり）
- **Sources Consulted**: リポジトリ内 `.github/workflows/ci.yml`, `.github/workflows/unit-test.yml`, `pyproject.toml`, `conftest.py`
- **Findings**:
  - `ci.yml`: `pip install -r requirements.txt`を実行するが、本リポジトリに`requirements.txt`は存在しない（pdmベースの`pyproject.toml`管理のみ）ため、依存関係インストールの時点で失敗する
  - `unit-test.yml`: トリガーが`branches: ["master"]`だが、GitHubリポジトリのデフォルトブランチは`main`であるため、`main`へのpush/PRでは発火しない
  - 両ワークフローとも`python_util`パッケージ自体をインストールしていない。リポジトリルートの`conftest.py`が`from python_util.test_evidence...`を直接importするため、パッケージが（editable等で）インストールされていない環境では`ModuleNotFoundError`が発生する
- **Implications**: 単なる修正ではなく、依存関係インストール手順・パッケージインストール・トリガー条件のすべてを見直した単一ワークフローへの置き換えが必要

### `codecov/codecov-action@v5` の入出力仕様
- **Context**: カバレッジ・テスト結果アップロードの正しい呼び出し方を確認する
- **Sources Consulted**: [codecov/codecov-action README](https://github.com/codecov/codecov-action), [Codecov GitHub Actions ドキュメント](https://about.codecov.io/tool/github-actions/)
- **Findings**:
  - 主要な入力: `token`（`CODECOV_TOKEN`シークレット参照）、`files`（アップロード対象ファイルパス、カンマ区切り）、`fail_ci_if_error`（既定`false`。アップロード失敗時にジョブを失敗させるか）、`report-type`（既定は暗黙的にカバレッジ。テスト結果をアップロードする場合は`test_results`を指定）
  - `codecov/test-results-action`は非推奨であり、公式移行手順は`codecov/codecov-action@v5`を`report-type: test_results`付きで追加呼び出しする方式
  - テスト結果アップロードステップは`if: ${{ !cancelled() }}`を付与し、テスト自体が失敗してもテスト結果はアップロードされるようにするのが公式サンプルのパターン（既存`ci.yml`にも同様の記述があった）
- **Implications**: カバレッジ用・テスト結果用の2回の`codecov/codecov-action@v5`呼び出しで要件2を満たす。`fail_ci_if_error: true`を両ステップに指定することで、アップロード失敗を要件2.4の「判別可能な形で示す」（ジョブ失敗として明示）に対応させる

### `codecov.yml`によるステータスチェックとしきい値運用
- **Context**: カバレッジしきい値(90%)を下回った場合にCIを失敗させる方法の選定
- **Sources Consulted**: [codecov.yml Reference](https://docs.codecov.com/docs/codecovyml-reference), [Status Checks](https://docs.codecov.com/docs/commit-status)
- **Findings**:
  - `codecov.yml`の`coverage.status.project.default.target`でしきい値を設定でき、Codecov側がコミットステータス（GitHub Checks）としてPRに反映する
  - ただし、このステータスチェックが実際に「マージをブロックする」ためには、GitHubリポジトリのブランチ保護設定で当該ステータスを必須チェックとして登録する必要があり、これは本スペックのコード変更では設定できないリポジトリ管理者のGitHub UI操作である
  - Codecovのステータス反映はアップロード後の非同期処理であり、CIジョブ自体の成否とは別のタイミング・別のチェック項目としてPR上に表示される
- **Implications**: 「CI Workflow shall 失敗ステータスを報告する」という要件3のAcceptance Criteriaを、外部SaaSの非同期処理とリポジトリ管理者の手動設定に依存させず、このリポジトリのCIジョブ自身の中で完結させるため、`pytest-cov`の`--cov-fail-under=90`オプション（テスト実行コマンド自体がしきい値未満で非ゼロ終了する標準機能）を採用する。`codecov.yml`によるステータスチェックのカスタマイズは本イテレーションでは導入しない（Non-Goalとして明記）

### `pdm-project/setup-pdm` によるpdmベースの依存関係インストール
- **Context**: 現行の生pipインストール（壊れている）に代わる、プロジェクトの標準パッケージ管理（pdm）に沿ったCI依存関係解決手段の選定
- **Sources Consulted**: [pdm-project/setup-pdm](https://github.com/pdm-project/setup-pdm)
- **Findings**:
  - `pdm-project/setup-pdm@v4`はPythonのセットアップとpdm自体のインストールを1ステップで行う公式アクション。`python-version`入力で対象バージョンを指定可能
  - `pdm install`はデフォルトでプロジェクト自体（editable）と依存関係グループを解決する。本リポジトリの`pyproject.toml`には`test`依存関係グループ（`pytest`, `pytest-cov`）が既に定義済み
  - `pdm.lock`がリポジトリにコミット済みであり、CI上での再現可能なインストールに利用できる
- **Implications**: `actions/setup-python` + 生`pip install`ではなく、`pdm-project/setup-pdm@v4` + `pdm install --group test`を採用することで、プロジェクト自体のインストール漏れ（現行の主要な不具合原因）を解消し、tech.mdの「pdmに統一」方針とも整合する

## Architecture Pattern Evaluation

| Option | Description | Strengths | Risks / Limitations | Notes |
|--------|-------------|-----------|---------------------|-------|
| 単一ワークフロー統合 + pdm + pytest-cov fail-under | 本設計で採用 | 依存関係・トリガー・カバレッジゲートが全て本リポジトリ内で完結し検証しやすい | 新規外部アクション(`pdm-project/setup-pdm`)への依存が増える | tech.mdのpdm方針と整合 |
| `codecov.yml`のステータスチェックのみでゲート | Codecov側の非同期ステータスに全面依存 | 設定はシンプル | ブランチ保護設定という本スペック外の手動作業に依存し、要件3の「CI失敗」を確実に満たせない | 不採用 |
| 2ワークフローを役割分担して存続 | push用/PR用等に分割 | - | 現状のいずれのワークフローも壊れており分担する実体的な理由がない。ユーザーヒアリングで統合が選好された | 不採用（ユーザー判断） |

## Design Decisions

### Decision: カバレッジゲートは`pytest-cov --cov-fail-under=90`をCIジョブ内で使用する
- **Context**: 要件3（カバレッジしきい値によるCIゲート）の実現方法
- **Alternatives Considered**:
  1. `codecov.yml`の`coverage.status.project.default.target: 90%` + GitHubブランチ保護での必須チェック化
  2. `pytest-cov`の`--cov-fail-under=90`をCI実行コマンドに追加
- **Selected Approach**: 2を採用。CIワークフローの`pdm run pytest`実行コマンドに`--cov-fail-under=90`を追加し、しきい値未満の場合はテスト実行ステップ自体が非ゼロ終了してジョブが失敗する
- **Rationale**: 本リポジトリのコード変更のみで完結し、外部SaaSの非同期処理やリポジトリ管理者による別途のブランチ保護設定に依存しない。要件3の「CI Workflow shall 失敗ステータスを報告する」を直接的・同期的に満たす
- **Trade-offs**: Codecov上のPRステータスチェック（コミットステータス）としての可視化は行わない（Non-Goal）。将来的にCodecov側の可視化が必要になった場合は別途`codecov.yml`を追加するスペックとして検討する
- **Follow-up**: `pyproject.toml`の`[tool.pytest.ini_options]`の既存`addopts`（html/term-missingレポート）は変更せず、CIワークフロー側のコマンドラインでのみ`--cov-report=xml --cov-fail-under=90`を追加する（ローカル開発時の挙動を変えないため）

### Decision: テスト結果アップロードは`codecov/test-results-action`ではなく`codecov/codecov-action@v5`の`report-type: test_results`を使用する
- **Context**: 要件2.2（テスト結果のCodecovアップロード）の実現方法
- **Alternatives Considered**:
  1. `codecov/test-results-action@v1`（既存`ci.yml`が使用していたアクション）
  2. `codecov/codecov-action@v5` + `report-type: test_results`
- **Selected Approach**: 2を採用
- **Rationale**: `test-results-action`は公式に非推奨とされ、`codecov-action@v5`への統合が推奨されている。新規に非推奨アクションを設置するのは本スペックの目的（中途半端な設定の解消）に反する
- **Trade-offs**: なし（推奨された移行先をそのまま採用）

### Decision: 依存関係インストールは`pdm-project/setup-pdm` + `pdm install`を採用する
- **Context**: 現行の壊れた`pip install -r requirements.txt`の置き換え
- **Alternatives Considered**:
  1. `actions/setup-python` + `pip install .`（`pyproject.toml`から直接installするだけの最小構成）
  2. `pdm-project/setup-pdm` + `pdm install --group test`
- **Selected Approach**: 2を採用
- **Rationale**: tech.mdで「パッケージ管理はpdmに統一」と明記されており、`pdm.lock`も既にコミット済みでロック済み依存解決が可能。ローカル開発と同一の依存関係解決経路をCIでも使うことで、ローカルでは通るがCIでは落ちる/その逆という差異を避けられる
- **Trade-offs**: 新規の外部アクション(`pdm-project/setup-pdm`)への依存が増えるが、公式にメンテナンスされているアクションであり許容範囲

## Synthesis Outcomes
- **Generalization**: 該当なし（単一のCIワークフロー統合という限定的スコープ）
- **Build vs Adopt**: 全面的にAdopt。`pdm-project/setup-pdm@v4`、`codecov/codecov-action@v5`（カバレッジ・テスト結果の両方）、`pytest-cov`の既存機能(`--cov-report=xml`, `--cov-fail-under`)をそのまま利用し、自作のスクリプトやカスタムアクションは導入しない
- **Simplification**: `codecov.yml`によるステータスチェックのカスタマイズを見送り、カバレッジゲートを`pytest-cov`のCLIオプションのみで完結させることで、外部SaaSの非同期処理とブランチ保護という本スペック外の手動設定への依存を排除した

## Risks & Mitigations
- 新規追加する`pdm-project/setup-pdm`アクションのメンテナンス状況変化（アーカイブ化・重大バージョン変更） — 公式`pdm-project` organizationが保守しており現時点でリスクは低いが、Revalidation Triggerとしてdesign.mdに明記する
- `CODECOV_TOKEN`シークレットが未登録・無効な場合、アップロードステップで認証エラーが発生する — 本スペックの前提（Adjacent expectations）として明記済み。ユーザーヒアリングにより登録済みと確認済み
- Codecov側でリポジトリが有効化されていない場合、アップロードは成功してもapp.codecov.io上にデータが反映されない可能性がある — 本スペックの管轄外（Out of Boundary）としてdesign.mdに明記する

## References
- [codecov/codecov-action](https://github.com/codecov/codecov-action) — 入力パラメータ・使用例
- [codecov/test-results-action](https://github.com/codecov/test-results-action) — 非推奨と移行先の案内
- [Codecov Test Analytics - Quick Start](https://docs.codecov.com/docs/test-analytics) — テスト結果アップロードの概要
- [codecov.yml Reference](https://docs.codecov.com/docs/codecovyml-reference) — ステータスチェック設定（本イテレーションでは不採用の根拠として参照）
- [pdm-project/setup-pdm](https://github.com/pdm-project/setup-pdm) — pdmベースのCIセットアップ手順
