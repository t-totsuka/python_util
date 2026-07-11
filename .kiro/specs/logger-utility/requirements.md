# Requirements Document

## Project Description (Input)

richをラップしたロガー機能の提供

- Logging Handlerで任意のファイルにログを書き出せる
- 呼び出し側のpyproject.tomlに設定を書くことで、ログファイルの書き出し場所・ログレベルの制御ができるようにしたい。
- 呼び出し側は複数のファイルやクラスで構成されるが書き出しのログファイルは1つまたは任意制御ができるようにしたい

## Introduction

本機能は、`rich` をラップしたロギングユーティリティを提供する。呼び出し側のアプリケーションは、`pyproject.toml` に設定を記述するだけでログの出力先ファイルとログレベルを制御できる。呼び出し側が複数のファイルやクラスから構成される場合でも、ログ出力先を単一ファイルに統合するか、モジュール/クラス単位で個別に制御するかを選択できることを目指す。

## Boundary Context (Optional)

- **In scope**: `rich` を用いたコンソール整形出力、ファイルハンドラによるログファイル書き出し、`pyproject.toml` からの設定読み込み（出力先パス・ログレベル）、複数呼び出し元でのロガーの一元化/個別制御
- **Out of scope**: ログローテーションの高度な制御（サイズ・世代管理などの詳細実装）、外部ログ収集基盤（ELK・CloudWatch等）との連携、Python以外のクライアントからの利用
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
</content>
