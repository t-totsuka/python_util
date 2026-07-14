# Requirements Document

## Project Description (Input)

richをラップしたロガー機能の提供

- Logging Handlerで任意のファイルにログを書き出せる
- 呼び出し側のpyproject.tomlに設定を書くことで、ログファイルの書き出し場所・ログレベルの制御ができるようにしたい。
- 呼び出し側は複数のファイルやクラスで構成されるが書き出しのログファイルは1つまたは任意制御ができるようにしたい

### 追加要望（Issue #7: ログのローテートの追加要望）

ログのローテーションの設定を追加したい。デフォルト動作は以下の通り。

- 1日ごとにログをローテーションする
- ログの保存期間は7日間
- ファイル名は「{ログの名前}-{日付}.log」
- 当日のログは「{ログの名前}.log」

## Introduction

本機能は、`rich` をラップしたロギングユーティリティを提供する。呼び出し側のアプリケーションは、`pyproject.toml` に設定を記述するだけでログの出力先ファイルとログレベルを制御できる。呼び出し側が複数のファイルやクラスから構成される場合でも、ログ出力先を単一ファイルに統合するか、モジュール/クラス単位で個別に制御するかを選択できることを目指す。

さらに、ファイル出力には日次のログローテーションを既定で適用する。当日のログは指定されたログファイルへ書き出し、日付が変わったログは日付付きのファイル名で退避し、保持期間（既定7日間）を超えた退避ファイルは自動削除する。ローテーションの無効化と保持日数の変更は `pyproject.toml` で制御できる。

## Boundary Context (Optional)

- **In scope**: `rich` を用いたコンソール整形出力、ファイルハンドラによるログファイル書き出し、`pyproject.toml` からの設定読み込み（出力先パス・ログレベル・ローテーション有効/無効・保持日数）、複数呼び出し元でのロガーの一元化/個別制御、日次ログローテーションと保持期間管理
- **Out of scope**: サイズベースのローテーション、日次以外のローテーション間隔（時間単位・週次など）、退避ファイル名規則のカスタマイズ、退避ログの圧縮・アーカイブ、外部ログ収集基盤（ELK・CloudWatch等）との連携、Python以外のクライアントからの利用
- **Adjacent expectations**: 本パッケージ（`python_util`）の既存方針（src レイアウト、snake_case命名、標準ライブラリ中心・軽量実装、pdmによるパッケージ管理）に準拠する

## Requirements

### Requirement 1: ロガー取得インターフェース

**Objective:** As a 呼び出し側の開発者, I want モジュールやクラス単位で簡単にロガーインスタンスを取得したい, so that 各所でロギングコードを重複させずに一貫した出力ができる

#### Acceptance Criteria

1. When 呼び出し側が名前を指定してロガー取得関数を呼び出す, the Logger Utility shall 指定された名前に紐づくロガーインスタンスを返す
2. If 呼び出し側が名前を省略した場合, then the Logger Utility shall 呼び出し元モジュール名をデフォルトのロガー名として使用する
3. The Logger Utility shall `rich` の出力フォーマットを用いてログメッセージをコンソールに整形出力する
4. When 同じロガー名でロガー取得関数が複数回呼び出される, the Logger Utility shall 同一の設定を持つロガーインスタンスを返す

### Requirement 2: ファイルへのログ書き出し

**Objective:** As a 呼び出し側の開発者, I want ログを任意のファイルに書き出したい, so that 実行後にログ内容を確認・保存できる

#### Acceptance Criteria

1. When ファイル出力用のロギングハンドラが設定される, the Logger Utility shall 指定されたファイルパスにログメッセージを書き出す
2. If 指定されたログファイルの出力先ディレクトリが存在しない場合, then the Logger Utility shall そのディレクトリを作成する
3. While ファイルハンドラが有効な間, the Logger Utility shall ログメッセージを対象ファイルへ追記する
4. Where コンソール出力とファイル出力の両方が有効な場合, the Logger Utility shall 同一のログメッセージを両方の出力先に書き出す

### Requirement 3: pyproject.tomlによる設定制御

**Objective:** As a 呼び出し側の開発者, I want pyproject.tomlに設定を記述するだけでログ出力先とログレベルを制御したい, so that コードを変更せずに環境ごとの挙動を調整できる

#### Acceptance Criteria

1. When Logger Utilityが初期化される, the Logger Utility shall 呼び出し側の`pyproject.toml`からロギング設定を読み込む
2. If `pyproject.toml`にログファイルの出力先パスが指定されている場合, then the Logger Utility shall そのパスにログファイルを出力する
3. If `pyproject.toml`にログレベルが指定されている場合, then the Logger Utility shall そのログレベルを適用する
4. If `pyproject.toml`にロギング設定が存在しない場合, then the Logger Utility shall あらかじめ定義されたデフォルトの出力先とログレベルを使用する
5. If `pyproject.toml`のロギング設定値が不正な形式である場合, then the Logger Utility shall 設定エラーを通知し、デフォルト設定にフォールバックする

### Requirement 4: 複数モジュール/クラス間でのログ出力の一元化・個別制御

**Objective:** As a 呼び出し側の開発者, I want 複数のファイルやクラスから利用してもログの出力先を1つに統合、または個別に制御したい, so that プロジェクト全体のログを一箇所で確認しつつ、必要な箇所だけ出力先を分けられる

#### Acceptance Criteria

1. Where 呼び出し側が単一のログファイルへの統合を設定で選択した場合, the Logger Utility shall すべてのモジュール・クラスからのログを同一のログファイルに書き出す
2. Where 呼び出し側がモジュールまたはクラス単位で個別のログ出力先を設定で指定した場合, the Logger Utility shall 該当するロガーのログのみを指定されたファイルに書き出す
3. The Logger Utility shall 同一プロセス内で同じロガーに対しハンドラを重複登録しない
4. When 複数のモジュールが同じロガー名でロガーを取得する, the Logger Utility shall 出力先設定を共有する

### Requirement 5: ログレベル制御

**Objective:** As a 呼び出し側の開発者, I want ログレベルを制御したい, so that 環境（開発/本番）に応じて出力量を調整できる

#### Acceptance Criteria

1. The Logger Utility shall DEBUG, INFO, WARNING, ERROR, CRITICALの標準ログレベルをサポートする
2. When 設定されたログレベルより低い重要度のログが記録される, the Logger Utility shall そのログメッセージを出力しない
3. Where コンソール出力とファイル出力で異なるログレベルが設定で指定されている場合, the Logger Utility shall それぞれの出力先に指定されたログレベルを個別に適用する

### Requirement 6: 日次ログローテーション

**Objective:** As a 呼び出し側の開発者, I want ログファイルを1日ごとにローテーションし、古いログを自動的に削除したい, so that ログファイルの肥大化を防ぎつつ直近のログを遡って確認できる

#### Acceptance Criteria

1. Where ファイル出力が有効な場合, the Logger Utility shall ローテーションを既定で有効として動作する
2. While ローテーションが有効な間, the Logger Utility shall 当日のログを設定された出力先ファイル（`{ログの名前}.log`）へ書き出す
3. When ローテーションが有効な状態で、直前のファイル書き込みから日付が変わった後に新たなログが記録される, the Logger Utility shall それまでの当日ファイルの内容を退避ファイルへ移し、新しい当日ファイルへの書き込みを開始する
4. The Logger Utility shall 退避ファイルの名前を `{ログの名前}-{日付}.log`（日付は退避対象ログが記録された日付、`YYYY-MM-DD` 形式）とする
5. When ローテーションが実行される, the Logger Utility shall 保持期間を超えた退避ファイルを削除する
6. The Logger Utility shall 退避ファイルの保持期間として既定で7日間を適用する
7. Where ロガー単位の個別ログファイルが設定で指定されている場合, the Logger Utility shall その個別ファイルにも同一のローテーション動作を適用する

### Requirement 7: ローテーションの設定制御

**Objective:** As a 呼び出し側の開発者, I want pyproject.tomlでローテーションの有効/無効と保持日数を制御したい, so that プロジェクトごとの運用方針に合わせてログ保持を調整できる

#### Acceptance Criteria

1. If `pyproject.toml`にローテーションを無効化する設定が指定されている場合, then the Logger Utility shall ローテーションおよび退避ファイルの削除を行わず、単一のログファイルへ追記し続ける
2. If `pyproject.toml`に保持日数が指定されている場合, then the Logger Utility shall 退避ファイルをその日数だけ保持する
3. If ローテーション関連の設定値が不正な形式である場合, then the Logger Utility shall 設定エラーを通知し、既定のローテーション設定（有効・保持7日間）にフォールバックする
