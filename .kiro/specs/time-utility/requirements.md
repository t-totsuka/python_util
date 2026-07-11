# Requirements Document

## Project Description (Input)
時間関係のutilityクラス
- 開発は主に日本なので、時間などは特に指定しない限りJSTを使いたい
- 標準モジュールだとロケール設定が煩雑なので楽にしたい

## Introduction
時間関連の処理を扱うユーティリティ機能を提供する。Python標準の `datetime` / `zoneinfo` / `locale` を直接扱う場合、JSTでの現在時刻取得や日本語形式での日時フォーマットのたびにタイムゾーン指定やロケール設定が必要となり煩雑になりがちである。本ユーティリティは、特に指定がない限りJST(Asia/Tokyo)をデフォルトのタイムゾーンとして扱うことで、日本国内向け開発における日時操作を簡潔にすることを目的とする。

## Boundary Context (Optional)
- **In scope**: JSTをデフォルトとした現在時刻取得、タイムゾーン変換(JST/UTC/任意のタイムゾーン間)、日時のフォーマットとパース、naive/awareなdatetimeの相互変換、不正入力時のエラーハンドリング
- **Out of scope**: 祝日判定・営業日計算などのカレンダー機能、スケジューリング/タイマー/定期実行機能、日本語以外のロケールでの曜日・月名表示
- **Adjacent expectations**: 既存の `python_util` パッケージの構成規約(`src/python_util/` 配下にモジュールを追加し、snake_case命名・pytestベースのテストを `tests/` にミラーリング配置)に従うこと

## Requirements

### Requirement 1: JST基準の現在時刻取得
**Objective:** As a 開発者, I want JSTでの現在時刻を簡単に取得したい, so that タイムゾーンを意識せずに日本時間を扱う処理を書ける

#### Acceptance Criteria
1. When 開発者が現在時刻取得関数を呼び出す, the TimeUtility shall JSTのタイムゾーン情報を持つawareなdatetimeオブジェクトを返す
2. The TimeUtility shall タイムゾーンを明示的に指定できるオプションを提供する
3. Where タイムゾーンが指定されない場合, the TimeUtility shall デフォルトでJST(Asia/Tokyo)を使用する

### Requirement 2: タイムゾーン変換
**Objective:** As a 開発者, I want 任意のdatetimeオブジェクトをJSTと相互変換したい, so that 外部システム(UTCなど)とのやり取りで発生するタイムゾーン変換を簡潔に行える

#### Acceptance Criteria
1. When 開発者がawareなdatetimeオブジェクトをJST変換関数に渡す, the TimeUtility shall そのdatetimeをJSTタイムゾーンに変換したオブジェクトを返す
2. When 開発者がnaiveなdatetimeオブジェクトをJST変換関数に渡す, the TimeUtility shall そのdatetimeをJSTのタイムゾーン情報を持つものとして扱いawareなdatetimeを返す
3. When 開発者がJSTのdatetimeをUTCへ変換する関数を呼び出す, the TimeUtility shall UTCタイムゾーンに変換したdatetimeオブジェクトを返す
4. When 開発者がJST以外の任意のタイムゾーンへの変換関数を呼び出す, the TimeUtility shall 指定されたタイムゾーンに変換したdatetimeオブジェクトを返す

### Requirement 3: 日時のフォーマットとパース
**Objective:** As a 開発者, I want ロケール設定なしで日本語形式の日時文字列を簡単に生成・解析したい, so that `locale.setlocale` などの煩雑な設定を避けて日時の文字列変換を行える

#### Acceptance Criteria
1. When 開発者がdatetimeオブジェクトをフォーマット関数に渡す, the TimeUtility shall ロケール設定なしで日本語表記(年月日・曜日等)を含む文字列を返す
2. The TimeUtility shall よく使われる日時フォーマット(例: `YYYY-MM-DD HH:MM:SS`, `YYYY年MM月DD日`)をあらかじめ指定可能な形で提供する
3. When 開発者が日時文字列をパース関数に渡す, the TimeUtility shall タイムゾーン情報を含まない文字列をJSTとして解釈したdatetimeオブジェクトを返す
4. If パース関数に不正な形式の文字列が渡された場合, then the TimeUtility shall 分かりやすいエラーメッセージとともに例外を送出する

### Requirement 4: naiveなdatetimeのJST既定扱い
**Objective:** As a 開発者, I want naiveなdatetimeを扱う際にJSTを前提とした振る舞いをさせたい, so that タイムゾーン未指定による意図しない挙動(UTC扱いなど)を避けられる

#### Acceptance Criteria
1. While 入力のdatetimeオブジェクトがnaiveである, the TimeUtility shall 特に指定がない限りJSTのタイムゾーン情報を持つものとして扱う
2. Where 開発者が明示的に別のタイムゾーンを指定した場合, the TimeUtility shall JSTではなく指定されたタイムゾーンを使用する

### Requirement 5: エラーハンドリング
**Objective:** As a 開発者, I want 不正な入力に対して明確なエラーを受け取りたい, so that 問題の原因を素早く特定しデバッグできる

#### Acceptance Criteria
1. If 存在しないタイムゾーン名が指定された場合, then the TimeUtility shall 不正なタイムゾーンであることを示す例外を送出する
2. If `None` や非対応の型がdatetime操作関数に渡された場合, then the TimeUtility shall 型エラーを示す例外を送出する
