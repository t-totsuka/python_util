# Implementation Plan

- [x] 1. Foundation: 依存関係とpytest実行設定の整備
- [x] 1.1 pytest-cov・pre-commitを依存関係に追加しカバレッジ計測用のpytest設定を行う
  - `dependency-groups.test` に `pytest-cov>=7.1.0` を追加する
  - 新規 `dependency-groups.dev` に `pre-commit>=4.6.0` を追加する
  - `[tool.pytest.ini_options]` の `addopts` に `--cov=src/python_util --cov-report=html:reports/coverage_html --cov-report=term-missing` を設定する
  - `pdm install` 後に `pdm run pytest` を実行し、`reports/coverage_html/index.html` が生成されることを確認する（観測可能な完了条件）
  - _Requirements: 3.6, 3.7_

- [x] 1.2 エビデンス成果物のGit管理範囲を.gitignoreに反映する
  - `.gitignore` に `reports/*` と `!reports/test-evidence.md` を追加する
  - `git status` で `reports/coverage_html/` 配下が追跡対象外、`reports/test-evidence.md` が追跡対象になることを確認する（観測可能な完了条件）
  - _Requirements: 3.1, 3.7_

- [x] 2. Foundation: 日本語テストメソッド命名規則の文書化
  - `test_(テスト目的)_(テスト対象)が_(状態)だった場合_(想定される結果)` を基本パターンとして定義し、テスト目的の分類（単体正常系/異常系/境界/結合など）と具体例をREADMEに記述する
  - 全角記号・空白を避けアンダースコアのみで区切るという、Pythonの識別子として有効な表記方法を明記する
  - 基本パターンは最低限の構成であり要素を追加できる旨、および本仕様完了後に `.kiro/steering/` へ別途反映される前提であることを明記する
  - README上に命名規則セクションが追加され、例文を含む説明が読める状態になっている（観測可能な完了条件）
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 4.1, 4.2_

- [x] 3. Foundation: test_evidenceサブパッケージの値オブジェクトと例外を定義する
- [x] 3.1 テスト結果を表す値オブジェクトを実装する
  - `TestOutcome`（`PASSED`/`FAILED`/`SKIPPED`/`ERROR` の4値を持つ列挙型）を実装する
  - イミュータブルな `TestCaseResult`（nodeid・メソッド名・サブパッケージ名・結果・実行時間・失敗内容を保持）を実装する
  - イミュータブルな `TestRunReport`（複数の `TestCaseResult` と実行開始・終了時刻を保持する集約）を実装する
  - 日本語命名規則に従ったテストメソッドで、各値オブジェクトの生成・不変性を検証し `pdm run pytest` が成功する（観測可能な完了条件）
  - _Requirements: 1.2, 3.2, 3.3, 3.4, 3.5_

- [x] 3.2 出力先検証用の例外を定義する
  - `.md` 以外の拡張子が指定された場合に送出する専用例外（`ValueError` 継承）を実装する
  - 日本語命名規則に従ったテストメソッドで例外メッセージと送出条件を検証し `pdm run pytest` が成功する（観測可能な完了条件）
  - _Requirements: 1.2, 3.7_

- [x] 4. Core: Markdownエビデンスのレンダリングと書き込みを実装する
- [x] 4.1 TestRunReportからMarkdownレポート文字列を描画する機能を実装する
  - サブパッケージ単位でテスト結果をグルーピングして見出し配下に列挙する
  - 合計/成功/失敗/スキップ件数と実行開始・終了時刻を含む全体サマリを先頭に出力する
  - 失敗・エラーとなったケースを、失敗内容とともに専用セクションに明示する
  - 0件（実行されたテストなし）の場合でも有効なMarkdownを返す
  - 日本語命名規則に従ったテストメソッドで、グルーピング・失敗セクション・0件時の出力を検証し `pdm run pytest` が成功する（観測可能な完了条件）
  - _Requirements: 1.2, 3.2, 3.3, 3.4, 3.5_
  - _Depends: 3.1_

- [x] 4.2 Markdownレポートをファイルへ書き込み公開APIを確定する
  - 描画結果を指定パスへ書き込み、親ディレクトリが存在しない場合は作成する機能を実装する
  - `.md` 以外の拡張子が指定された場合に専用例外を送出し、書き込みを行わないことを保証する
  - `test_evidence` パッケージの `__init__.py` で公開APIを `__all__` により限定エクスポートする
  - 日本語命名規則に従ったテストメソッドで、正常書き込み・不正拡張子時の例外送出・公開APIのエクスポートを検証し `pdm run pytest` が成功する（観測可能な完了条件）
  - _Requirements: 1.2, 3.1, 3.7_

- [x] 5. Core: conftest.pyによるpytest結果収集とエビデンス出力を統合する
- [x] 5.1 pytestフックで3フェーズの結果を集約しテストケース結果を生成する
  - `pytest_runtest_logreport` で `setup`/`call`/`teardown` 各フェーズの結果をnodeid単位で一時保持し、いずれかが失敗なら`FAILED`、`setup`が`skipped`なら`SKIPPED`、すべて成功なら`PASSED`として確定する
  - nodeidを `::` で分割し、最初のセグメントからサブパッケージ名（`tests/` 直下のディレクトリ名）を抽出し、最後のセグメントを `method_name` としてパラメータ接尾辞（`[param0]`等）を含めたまま保持する
  - 確定した結果から `TestCaseResult` を生成しセッション内リストへ追加する
  - `pytester` フィクスチャを用いたテストで、`call`成功後に`teardown`が失敗するケースが`FAILED`として記録されることを確認する（観測可能な完了条件、Requirement 3.4の正確性を担保）
  - _Requirements: 1.2, 3.2, 3.3, 3.4, 3.5_
  - _Depends: 3.1_

- [x] 5.2 セッション終了時にエビデンスファイルを書き出す
  - `pytest_sessionstart` でセッション開始時刻を記録する
  - `pytest_sessionfinish` でセッション終了時刻を記録し、収集済みの `TestCaseResult` 群から `TestRunReport` を組み立てて `reports/test-evidence.md` へ書き込む
  - `pdm run pytest` 実行のみ（追加のコマンドオプションや設定変更なし）でエビデンスが自動生成されることを確認する（観測可能な完了条件）
  - _Requirements: 1.2, 3.1, 3.7, 4.3_
  - _Depends: 4.2, 5.1_

- [x] 6. Integration: pre-commitによるコミット前フルスイート強制を実装する
  - リポジトリルートに `.pre-commit-config.yaml` を新設し、`repo: local` / `language: system` のフックとして `pdm run pytest && git add reports/test-evidence.md` を `entry` に設定する（`pass_filenames: false`, `always_run: true`）
  - `pdm run pre-commit install` の実行によりGitフックとして有効化されることを確認する
  - フィルタなしのフルスイートが失敗した場合にフックが非0で終了しコミットがブロックされ、成功した場合は `reports/test-evidence.md` がステージされてコミットに含まれることをローカル実行で確認する（観測可能な完了条件）
  - _Requirements: 3.1, 3.7, 4.3_
  - _Depends: 1.1, 5.2_

- [x] 7. Core: 既存テストメソッド名を日本語命名規則へ改修する（サブパッケージ別）
- [x] 7.1 (P) loggingサブパッケージの既存テストメソッド名を日本語命名規則へ改修する
  - `tests/logging/` 配下の全 `test_` メソッド名を基本パターンに沿って改修する（アサーション・テストロジックは変更しない）
  - 他のテストやフィクスチャからメソッド名で参照されている箇所があれば追従して更新する
  - `pdm run pytest tests/logging/` を実行し、改修前と同じ成功/失敗結果になることを確認する（観測可能な完了条件）
  - _Requirements: 1.2, 1.6, 2.1, 2.2, 2.3, 2.4, 4.1_
  - _Boundary: tests/logging_
  - _Depends: 2_

- [x] 7.2 (P) time_utilityサブパッケージの既存テストメソッド名を日本語命名規則へ改修する
  - `tests/time_utility/` 配下の全 `test_` メソッド名を基本パターンに沿って改修する（アサーション・テストロジックは変更しない）
  - 他のテストやフィクスチャからメソッド名で参照されている箇所があれば追従して更新する
  - `pdm run pytest tests/time_utility/` を実行し、改修前と同じ成功/失敗結果になることを確認する（観測可能な完了条件）
  - _Requirements: 1.2, 1.6, 2.1, 2.2, 2.3, 2.4, 4.1_
  - _Boundary: tests/time_utility_
  - _Depends: 2_

- [x] 7.3 (P) binary_string_codecサブパッケージの既存テストメソッド名を日本語命名規則へ改修する
  - `tests/binary_string_codec/` 配下の全 `test_` メソッド名を基本パターンに沿って改修する（アサーション・テストロジックは変更しない）
  - `@pytest.mark.parametrize` を使用しているテストについても、パラメータ定義を変更せずメソッド名のみ改修する
  - 他のテストやフィクスチャからメソッド名で参照されている箇所があれば追従して更新する
  - `pdm run pytest tests/binary_string_codec/` を実行し、改修前と同じ成功/失敗結果になることを確認する（観測可能な完了条件）
  - _Requirements: 1.2, 1.6, 2.1, 2.2, 2.3, 2.4, 4.1_
  - _Boundary: tests/binary_string_codec_
  - _Depends: 2_

- [x] 7.4 (P) progress_displayサブパッケージの既存テストメソッド名を日本語命名規則へ改修する
  - `tests/progress_display/` 配下の全 `test_` メソッド名を基本パターンに沿って改修する（アサーション・テストロジックは変更しない）
  - 他のテストやフィクスチャからメソッド名で参照されている箇所があれば追従して更新する
  - `pdm run pytest tests/progress_display/` を実行し、改修前と同じ成功/失敗結果になることを確認する（観測可能な完了条件）
  - _Requirements: 1.2, 1.6, 2.1, 2.2, 2.3, 2.4, 4.1_
  - _Boundary: tests/progress_display_
  - _Depends: 2_

- [x] 8. Validation: エビデンス生成・カバレッジ・pre-commitフックの統合検証
- [x] 8.1 pytesterでconftest.pyのnodeid解析を検証する
  - `pytester` フィクスチャで `@pytest.mark.parametrize` を用いたサンプルテストを実行し、`[param0]` 等の接尾辞を含むnodeidが `method_name` にそのまま反映されることを確認する
  - `pytester` フィクスチャで小さなサンプルスイートを実行し、`reports/test-evidence.md` が生成されサブパッケージ別グルーピング・失敗セクションを含むことを確認する（観測可能な完了条件）
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_
  - _Depends: 5.2_

- [x] 8.2 pre-commitフックの成功時ステージングと失敗時ブロックを検証する
  - 全テスト成功時に `.pre-commit-config.yaml` のフックが `reports/test-evidence.md` をステージすることを確認する
  - いずれかのテストを意図的に失敗させ、フックが非0で終了しコミットがブロックされることを確認する（観測可能な完了条件）
  - _Requirements: 3.1, 3.7_
  - _Depends: 6_

- [x] 8.3 pytest-cov設定によるHTMLカバレッジレポート生成を確認する
  - `pdm run pytest` 実行後に `reports/coverage_html/index.html` が生成され、`src/python_util` 配下の各サブパッケージの行カバレッジがモジュール別に確認できることを確認する（観測可能な完了条件）
  - _Requirements: 3.6_
  - _Depends: 1.1_

- [x] 9. Validation: 全体回帰確認とREADME更新
- [x] 9.1 4サブパッケージ全体でpdm run pytestを実行し改修前後の結果が一致することを確認する
  - `pdm run pytest` をフィルタなしで実行し、全サブパッケージのテストが成功することを確認する
  - 生成された `reports/test-evidence.md` に日本語命名規則へ改修済みのテストメソッド名がそのまま含まれていることを確認する（観測可能な完了条件）
  - _Requirements: 2.2, 2.4, 3.5_
  - _Depends: 7.1, 7.2, 7.3, 7.4_

- [x] 9.2 READMEにテスト命名規則・エビデンス生成・pre-commitセットアップ手順を追記する
  - テストエビデンス（`reports/test-evidence.md` / `reports/coverage_html/index.html`）の生成方法を追記する
  - `pdm run pre-commit install` によるセットアップ手順を追記する
  - README上の該当セクションを読むだけでエビデンス生成とコミット前フックのセットアップが再現できる状態になっている（観測可能な完了条件）
  - _Requirements: 3.1, 3.7_
  - _Depends: 8.1, 8.2, 8.3, 9.1_
