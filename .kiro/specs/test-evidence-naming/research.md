# Research & Design Decisions Template

## Summary

- **Feature**: `test-evidence-naming`
- **Discovery Scope**: Extension（既存のpytestベースのテスト基盤への追加）
- **Key Findings**:
  - 既存の `dependency-groups.test` には `pytest>=9.1.1` のみが存在し、カバレッジ計測用の依存関係は未導入
  - `.kiro/steering/tech.md` は「標準ライブラリ中心、外部依存は必要最小限」を明言しており、Markdownエビデンス生成に新規外部ライブラリ（例: `pytest-md-report`）を追加するのは方針に反する。pytestの標準フック（`pytest_runtest_logreport` / `pytest_sessionfinish`）で自作する方が既存方針に沿う
  - HTMLカバレッジレポートは `pytest-cov`（デファクトスタンダード、`coverage.py` をラップ）の導入で標準的に実現できる。バージョン互換性を確認済み
  - 設計レビューでの指摘（部分実行によるエビデンス上書きリスク）を受け、`pre-commit` フレームワークでフルスイート実行をコミット前に強制する方式を追加採用

## Research Log

### pre-commitフレームワークのバージョンと互換性

- **Context**: フルスイートのテストをコミット直前に強制実行し、成功時のみMarkdownエビデンスをコミットに含める仕組み（設計レビューのCritical Issue 2への対応、ユーザー確認済み）として `pre-commit` フレームワークの採用を検討
- **Sources Consulted**: [pre-commit · PyPI](https://pypi.org/project/pre-commit/)
- **Findings**:
  - 最新版: `4.6.0`（2026-04-21リリース）
  - `requires-python`: `>=3.10`（本プロジェクトの `requires-python = ">=3.11"` と両立）
  - `language: system` の `repo: local` フックを使うことで、`pre-commit` 自体が個別言語環境を構築せず、既存の `pdm` 環境の `pytest` をそのまま呼び出せる
- **Implications**: `dependency-groups` に新規 `dev` グループを設け `pre-commit>=4.6.0` を追加。リポジトリルートに `.pre-commit-config.yaml` を新設し、`pdm run pytest`（フィルタなしのフルスイート）の実行と、成功時の `git add reports/test-evidence.md` を1つのローカルフックとして定義する

### pytest-cov のバージョンと互換性

- **Context**: 要件3.6（HTML形式のカバレッジレポート）を満たす手段として `pytest-cov` の採用を検討
- **Sources Consulted**: [PyPI JSON API (pytest-cov)](https://pypi.org/pypi/pytest-cov/json)
- **Findings**:
  - 最新版: `7.1.0`（2026-03-21リリース）
  - `requires-python`: `>=3.9`（本プロジェクトの `requires-python = ">=3.11"` と両立）
  - 依存: `pytest>=7`（本プロジェクトの `pytest>=9.1.1` と両立）、`coverage>=7.10.6`
- **Implications**: `dependency-groups.test` に `pytest-cov>=7.1.0` を追加すれば、`--cov-report=html` オプションのみでHTMLカバレッジレポートが生成できる。追加のカスタム実装は不要

### Markdownエビデンス生成の実現方式

- **Context**: 要件3.1〜3.5（Markdown形式のテスト結果レポート）をどう実装するか。既製のpytestプラグイン（`pytest-md-report` 等）を使うか、自作するかを検討
- **Sources Consulted**: 既存コードベースの `tests/` 構成、`.kiro/steering/tech.md`（外部依存最小化の方針）
- **Findings**:
  - `pytest-md-report` 等の既製プラグインはテスト名・結果の一覧は出力できるが、本プロジェクト独自の「日本語命名規則に基づくテスト目的の分類」や「サブパッケージ単位のグルーピング」には対応しない
  - pytestは標準で `pytest_runtest_logreport(report)` フックと `pytest_sessionfinish(session)` フックを提供しており、これらだけで各テストの結果（outcome, duration, nodeid）を収集できる（追加ライブラリ不要）
  - `tests/<subpackage>/...` というディレクトリ構成（`structure.md` で規定済み）から、nodeidの2階層目（`tests/` の直下）を抽出するだけでサブパッケージ名を機械的に判定できる
- **Implications**: Markdownレポート生成は `python_util.test_evidence` サブパッケージ内に型安全な純粋関数として実装し、収集用のpytestフックはリポジトリルートの `conftest.py` に配置する（他プロジェクトへの再配布を想定しない、本リポジトリ固有の開発フロー）

### 既存サブパッケージとの一貫性確認

- **Context**: 新設する `test_evidence` サブパッケージが既存の `logging` / `time_utility` / `progress_display` と同じ構成パターンに従えるか確認
- **Sources Consulted**: `src/python_util/progress_display/`, `.kiro/steering/structure.md`, `.kiro/steering/tech.md`
- **Findings**:
  - 既存サブパッケージは共通して `types.py`（値オブジェクト）/ `exceptions.py`（`ValueError` 継承の専用例外）/ `__init__.py`（`__all__` による公開API限定）のパターンを採用
  - 例外はサブパッケージ内部限定のものは先頭アンダースコアを付す規約がある
- **Implications**: `test_evidence` サブパッケージも同一パターンを踏襲する。ただし pytest フック実装自体（`conftest.py`）は「利用側コードから直接インポートされる公開API」ではないため、サブパッケージの外（リポジトリルート）に置き、サブパッケージ内は純粋なデータ型とレンダリング関数のみとする

## Architecture Pattern Evaluation

| Option | Description | Strengths | Risks / Limitations | Notes |
|--------|-------------|-----------|---------------------|-------|
| 自作フック + 型安全な純粋関数（採用） | `conftest.py` のpytestフックで収集し、`python_util.test_evidence` の純粋関数でMarkdownを描画 | 外部依存を増やさない、サブパッケージとして単体テスト可能、既存パターンと整合 | フック実装自体はpytest内部APIに依存するため`pytest`のメジャーバージョンアップで調整が必要になり得る | `tech.md` の外部依存最小化方針に合致 |
| 既製プラグイン（`pytest-md-report` 等）採用 | サードパーティプラグインでMarkdown表を出力 | 実装コストが低い | 日本語命名規則に基づく分類・サブパッケージ別グルーピングに対応しない、外部依存追加は方針に反する | 不採用 |

## Design Decisions

### Decision: Markdownエビデンスとカバレッジ収集の責務分離

- **Context**: 要件3は「テスト結果Markdown」と「HTMLカバレッジ」の2種類のエビデンスを求めている
- **Alternatives Considered**:
  1. 単一のカスタムプラグインで両方を自作する
  2. カバレッジは `pytest-cov`（既製ツール）に任せ、Markdownのみ自作する
- **Selected Approach**: 2を採用。カバレッジ計測・HTML描画は `pytest-cov` に委譲し、`pyproject.toml` の `addopts` で `--cov` 系オプションを設定するのみとする。Markdown生成のみを本リポジトリの責務として実装する
- **Rationale**: カバレッジ計測（行網羅判定、HTML描画）は `coverage.py` が長年の実績を持つデファクトスタンダードであり、車輪の再発明を避けられる。一方Markdown側は本プロジェクト固有の要件（日本語命名規則・サブパッケージ別分類）があるため自作が妥当
- **Trade-offs**: `pytest-cov` という新規外部依存が1つ増えるが、`tech.md` が許容する「必要最小限の外部依存」の範囲内と判断
- **Follow-up**: 実装時に `--cov` の対象パス（`src/python_util`）とレポート出力先ディレクトリを `pyproject.toml` に明示する

### Decision: エビデンス出力先ディレクトリとGit管理範囲

- **Context**: Markdownレポート・HTMLカバレッジレポートの出力先、および両者をGit管理下に置くかどうかを決める必要がある
- **Alternatives Considered**:
  1. `tests/` 配下に出力する
  2. リポジトリルート直下に `reports/` ディレクトリを新設して出力し、`reports/test-evidence.md` のみGit管理下に置く（`reports/coverage_html/` は `.gitignore` 対象のまま）
  3. `reports/` 配下の成果物（Markdown・HTML）を両方ともGit管理下に置く
- **Selected Approach**: 2を採用。`.gitignore` に `reports/*` と `!reports/test-evidence.md` を追加し、Markdownレポートのみを追跡対象とする
- **Rationale**: `tests/` は `src/python_util/` をミラーリングするソースツリーであり、実行結果の成果物（生成物）を混在させると `structure.md` の既存規約と衝突するため生成物専用ディレクトリに分離する。HTMLカバレッジは多数のファイルから成りコミットごとの差分が大きくリポジトリを肥大化させるため追跡対象から除外する一方、Markdownエビデンスはコミット単位の証跡として軽量かつ有用なためGit管理下に置く（ユーザー確認済み）
- **Trade-offs**: 新しいトップレベルディレクトリが増える。Markdownレポートはコミットのたびに差分が発生する
- **Follow-up**: `.gitignore` に `reports/*` / `!reports/test-evidence.md` を追加する

### Decision: pre-commitによるフルスイート強制実行とエビデンスのコミット同梱

- **Context**: 設計レビューで指摘された「フィルタ実行（`-k`等）が `reports/test-evidence.md` を無条件に上書きし、部分実行結果が全体エビデンスとして誤認されるリスク」（Critical Issue 2）への対応
- **Alternatives Considered**:
  1. Markdownレポート内に実行範囲（全件/部分）を記載するのみで運用上の注意に留める
  2. `pre-commit` フレームワークでコミット直前にフルスイートを強制実行し、成功時のみ生成物をコミットに含める
  3. 素のGitフック（`.githooks/`）で同様の制御を行う
- **Selected Approach**: 2を採用（ユーザー確認済み）。`repo: local` / `language: system` のフックとして `pdm run pytest`（フィルタなし）を実行し、失敗時はコミットをブロックする。成功時は `git add reports/test-evidence.md` をフック内で実行し、生成された最新のフルスイート結果を同一コミットに含める
- **Rationale**: コミットに残るMarkdownエビデンスが常に「フルスイート実行かつ全件成功」の結果であることをGitフックで機械的に保証できる。開発中の部分実行（`pytest tests/logging/`等）はローカルの `reports/test-evidence.md` を一時的に上書きするが、コミットが成立する時点では必ずフルスイートの結果に置き換わるため、Critical Issue 2の懸念が解消される
- **Trade-offs**: `pre-commit` という新規開発依存が1つ増える（`tech.md` の外部依存最小化方針からは逸脱するが、実行時依存ではなく開発フロー専用ツールであり、業界標準としての採用価値がユーザーの意向により優先された）。コミットのたびにフルスイートが実行されるため、変更規模によってはコミット所要時間が増える
- **Follow-up**: 実装時に `.pre-commit-config.yaml` のフック定義（`entry`, `pass_filenames: false`, `always_run: true`）を確定し、READMEにセットアップ手順（`pdm run pre-commit install`）を追記する

## Risks & Mitigations

- pytestの内部フックAPI（`pytest_runtest_logreport` 等）は将来のメジャーバージョンで変更される可能性がある — 影響範囲を `conftest.py` に限定し、`test_evidence` サブパッケージ本体（型・レンダリング関数）への影響を避ける設計とすることで緩和
- 既存テストメソッド名を日本語に改修する際、他のテストやフィクスチャからメソッド名で参照されているケースを見落とすリスク — `pdm run pytest` によるテスト成功確認を移行の完了条件とすることで緩和（要件2.2）
- `pre-commit` フックの導入により、フルスイートの実行時間がコミット所要時間に直結する — 現時点のテスト件数・実行時間は小さく実用上の支障はないが、将来テストが大幅に増えた場合は再検討が必要

## References

- [pytest-cov · PyPI](https://pypi.org/project/pytest-cov/) — 最新バージョン・依存関係の確認
- [pytest-cov 7.1.0 documentation](https://pytest-cov.readthedocs.io/) — `--cov-report=html` オプションの仕様確認
- [pre-commit · PyPI](https://pypi.org/project/pre-commit/) — 最新バージョン・Python要件の確認
