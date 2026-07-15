# Implementation Plan

- [x] 1. Foundation: 重複ワークフローの整理とCI骨格の構築
  - `.github/workflows/unit-test.yml`を削除する
  - `.github/workflows/ci.yml`を全面的に書き換え、`main`へのpushおよび`main`向けPRをトリガーとする
  - `actions/checkout`によるリポジトリのチェックアウトステップを、`pdm-project/setup-pdm`によるセットアップより前に配置する
  - `pdm-project/setup-pdm`によるPython/pdmセットアップと`pdm install --group test`による依存関係インストールのステップを構築する
  - 観測可能な完了状態: 検証用ブランチへのpushでワークフローが起動し、チェックアウト・pdmセットアップ・依存関係インストールの各ステップまで成功する(この時点ではテスト実行ステップは未実装のため後続タスクで検証)
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.6_
  - _Boundary: CI Workflow Definition_

- [x] 2. Core: テスト実行・カバレッジゲート・READMEバッジ
- [x] 2.1 (P) カバレッジ計測付きテスト実行とカバレッジしきい値ゲートを構築する
  - `ci.yml`のテスト実行ステップで`pdm run pytest`にカバレッジXML出力(`--cov-report=xml`)・JUnit出力(`--junitxml=junit.xml`)・カバレッジしきい値(`--cov-fail-under=90`)を追加する
  - 既存`pyproject.toml`の`addopts`(html/term-missingレポート)はローカル開発用として変更しない
  - 観測可能な完了状態: 検証用ブランチでワークフローを実行し、`coverage.xml`と`junit.xml`が生成され、現状カバレッジ(約99%)ではテスト実行ステップが成功することを確認する
  - _Requirements: 1.5, 3.1, 3.2, 3.3_
  - _Boundary: CI Workflow Definition_
  - _Depends: 1_

- [x] 2.2 (P) READMEにCodecovバッジを追加する
  - README.mdのタイトル直下にCodecovのカバレッジバッジのMarkdown画像リンクを追加する
  - バッジ画像はapp.codecov.io上の当該リポジトリのカバレッジダッシュボードへのリンクを持つ
  - 観測可能な完了状態: README.mdをGitHub上でレンダリングした際にバッジ画像が表示され、クリックでapp.codecov.ioのダッシュボードへ遷移する
  - _Requirements: 4.1, 4.2_
  - _Boundary: README Badge_

- [x] 3. Integration: Codecovアップロードステップの統合
  - `ci.yml`に`codecov/codecov-action@v5`を用いたカバレッジアップロードステップ(`token: secrets.CODECOV_TOKEN`, `files: ./coverage.xml`, `fail_ci_if_error: true`)を追加する
  - 同様に`report-type: test_results`を指定したテスト結果アップロードステップ(`files: ./junit.xml`, `if: ${{ !cancelled() }}`, `fail_ci_if_error: true`)を追加する
  - 観測可能な完了状態: 検証用ブランチでのワークフロー実行後、app.codecov.io上に当該コミットのカバレッジレポートとテスト結果が反映される
  - _Requirements: 2.1, 2.2, 2.3, 2.4_
  - _Boundary: Codecov Upload Steps_
  - _Depends: 2.1_

- [x] 4. Validation: CIワークフローの動作検証
- [x] 4.1 検証用PRでのCIワークフロー正常系動作を確認する
  - 検証用ブランチ・PRを作成し、`main`向けPRでワークフローが自動起動することを確認する
  - チェックアウト・pdmセットアップ・依存関係インストール・テスト実行・カバレッジ/テスト結果アップロード・README上のバッジ表示までの一連の流れがすべて成功することを確認する
  - 観測可能な完了状態: 検証用PRのGitHub ActionsタブでCIワークフローが成功ステータスで完了し、app.codecov.io上にレポートが反映され、README.mdのバッジが正しく表示される
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 2.1, 2.2, 2.3, 2.4, 4.1, 4.2_
  - _Depends: 3, 2.2_

- [x] 4.2 カバレッジしきい値ゲートの発火を検証する
  - 検証用コミットで一時的に`--cov-fail-under`を実カバレッジより高い値に設定し、テスト実行ステップおよびジョブ全体が失敗することを確認する
  - 検証後、しきい値を90%に戻す
  - 観測可能な完了状態: 一時的な検証コミットのCI実行でジョブが失敗ステータスとなり、90%へ戻した後は成功することを確認する
  - _Requirements: 3.1, 3.2, 3.3_
  - _Depends: 2.1_

## Implementation Notes

- タスク3で`codecov/codecov-action@v5`の入力キーを`report-type`(ハイフン)と記述したが、実際の入力スキーマは`report_type`(アンダースコア)であり、GitHub Actions上で`Unexpected input(s) 'report-type'`という警告が発生し、テスト結果アップロードが`report_type`未指定の状態(既定のカバレッジアップロード扱い)で実行されていた。タスク4.1の実PR検証で発覚し、`report_type`へ修正した。ローカルのYAML構文チェックだけではこの種の「有効なYAMLだがアクションの入力スキーマとしては無効なキー」は検出できないため、CI設定タスクでは実際にワークフローを1度トリガーしてActionsのログ・Annotationsを確認するまでは完了とみなさないこと
