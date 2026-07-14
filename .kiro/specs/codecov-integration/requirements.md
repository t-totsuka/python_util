# Requirements Document

## Project Description (Input)

GitHubでapp.codecov.ioに対応したい。

現状:

- リポジトリシークレット(`CODECOV_TOKEN`)をGitHubに登録済み
- `.github/workflows/`に`ci.yml`と`unit-test.yml`の2つのワークフローファイルが存在するが、いずれも中途半端な設置状態
  - `ci.yml`は`pip install -r requirements.txt`を実行するが、本リポジトリに`requirements.txt`は存在しない(pdmベースの`pyproject.toml`管理)
  - `unit-test.yml`は`branches: ["master"]`でトリガーされるが、デフォルトブランチは`main`のため実質発火しない
  - どちらもプロジェクト自体(`python_util`パッケージ)をインストールしておらず、`conftest.py`が`import python_util...`することに失敗する可能性が高い
  - `codecov.yml`設定ファイルは未整備
- README.mdにCodecovバッジが未設置

## Introduction

本機能は、GitHub Actions上でのテスト実行結果とカバレッジ計測をCodecov(app.codecov.io)へ連携し、README上でカバレッジ状況を可視化するCI連携基盤を提供する。現在重複・中途半端な状態にある2つのワークフロー定義を、正しく動作する単一のCIワークフローに整理し、カバレッジしきい値によるゲート、Codecovへのカバレッジ・テスト結果アップロード、READMEへのバッジ表示を実現する。

## Boundary Context (Optional)

- **In scope**: 重複するCIワークフロー定義の単一ワークフローへの整理、`main`ブランチへのpushおよび`main`向けプルリクエストでの自動実行、Codecovへのカバレッジレポート・テスト結果(JUnit)アップロード、カバレッジしきい値(90%)によるCI成否判定、README上のCodecovバッジ表示
- **Out of scope**: `CODECOV_TOKEN`シークレット自体の発行・登録（GitHub側で作業済み）、app.codecov.io上でのリポジトリ有効化・プロジェクト設定自体（Codecov側で完了している前提）、Lint(ruff)等カバレッジ以外の品質チェックのCIへの追加、複数Pythonバージョンでのテストマトリクス化、リリース・デプロイ自動化
- **Adjacent expectations**: 本機能はGitHubリポジトリに`CODECOV_TOKEN`シークレットが既に登録されていること、および対象リポジトリがCodecov側で認識・有効化されていることを前提とする。これらが未整備の場合、本機能が提供するワークフローはアップロードステップで認証エラーとなる

## Requirements

### Requirement 1: 単一CIワークフローへの整理

**Objective:** As a リポジトリメンテナー, I want 重複・中途半端な状態にある2つのワークフロー定義を1つの正しく動作するCIワークフローに整理したい, so that テスト実行とカバレッジ計測が確実かつ一貫して行われ、無駄な重複実行や壊れた設定が残らないようにできる

#### Acceptance Criteria

1. The CI Workflow shall テスト実行とカバレッジ計測を単一の実行系統としてのみ提供し、重複した並行実行を発生させない
2. When `main`ブランチへコードがpushされる, the CI Workflow shall 自動的に実行される
3. When `main`ブランチ向けのプルリクエストが作成または更新される, the CI Workflow shall 自動的に実行される
4. The CI Workflow shall プロジェクトの依存関係定義に基づいて依存関係を解決・インストールする
5. The CI Workflow shall プロジェクトのテストスイートをカバレッジ計測付きで実行する
6. If 依存関係のインストールまたはテストスイートの実行に失敗した場合, then the CI Workflow shall 失敗ステータスを報告する

### Requirement 2: Codecovへのカバレッジ・テスト結果アップロード

**Objective:** As a リポジトリメンテナー, I want CI実行時にカバレッジ結果とテスト結果をCodecovへ自動アップロードしたい, so that app.codecov.io上でカバレッジ推移とテスト結果を可視化・追跡できる

#### Acceptance Criteria

1. When CI Workflowがテストスイートの実行を完了する, the CI Workflow shall カバレッジレポートをCodecovへアップロードする
2. When CI Workflowがテストスイートの実行を完了する, the CI Workflow shall テスト結果(JUnit形式)をCodecovへアップロードする
3. The CI Workflow shall 登録済みのリポジトリシークレット(`CODECOV_TOKEN`)を用いてCodecovへの認証を行う
4. If Codecovへのアップロードが認証エラーまたは通信エラーで失敗した場合, then the CI Workflow shall その失敗をCI実行結果・ログ上で判別可能な形で示す

### Requirement 3: カバレッジしきい値によるCIゲート

**Objective:** As a リポジトリメンテナー, I want カバレッジ率が一定のしきい値を下回った場合にCIを失敗させたい, so that カバレッジの劣化をマージ前に検知できる

#### Acceptance Criteria

1. The CI Workflow shall カバレッジしきい値として90%を適用する
2. While カバレッジ率がしきい値(90%)以上である間, the CI Workflow shall 成功ステータスを報告する
3. If カバレッジ率がしきい値(90%)を下回った場合, then the CI Workflow shall 失敗ステータスを報告する

### Requirement 4: READMEへのCodecovバッジ表示

**Objective:** As a リポジトリ閲覧者, I want README上でカバレッジ状況を一目で確認したい, so that プロジェクトの品質状態を素早く把握できる

#### Acceptance Criteria

1. The README shall 対象リポジトリのCodecovカバレッジバッジを表示する
2. When 閲覧者がREADME上のバッジをクリックする, the README shall app.codecov.io上の当該リポジトリのカバレッジダッシュボードへのリンクを提供する
