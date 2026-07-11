# Implementation Plan

- [ ] 1. Foundation: パッケージ基盤とエラー型
- [x] 1.1 パッケージ雛形とtzdata依存の追加
  - `src/python_util/time_utility/` パッケージを作成し、公開シンボルをまだ持たない `__init__.py` を配置する
  - `tests/time_utility/` を既存 `tests/logging/` と同じミラーリング構成で初期化する
  - `pyproject.toml` の依存関係に `tzdata`(`sys_platform == "win32"` 限定)を追加する
  - Observable: `pdm install` が成功し、`import python_util.time_utility` がエラーなく実行できる
  - _Requirements: 1.3_

- [x] 1.2 例外モジュール実装
  - `InvalidTimezoneError` と `DateTimeParseError` を `ValueError` のサブクラスとして実装する
  - 各例外が問題となった入力値を含むメッセージを保持できることを確認する
  - Observable: 両例外をraiseし、メッセージに入力値が含まれることを検証するユニットテストがパスする
  - _Requirements: 5.1, 5.2_

- [x] 2. タイムゾーン解決の実装
  - JST定数(`ZoneInfo("Asia/Tokyo")`)を唯一の真実源として定義する
  - 文字列/`tzinfo`/`None` を受け取り `tzinfo` へ解決する関数を実装し、`None` の場合は常にJSTへ解決する
  - 存在しないタイムゾーン名や非対応の型が渡された場合、`InvalidTimezoneError` を送出する
  - Observable: タイムゾーン未指定でJSTが解決され、`"Asia/Tokio"` のような不正な名前で `InvalidTimezoneError` が送出されることを検証するユニットテストがパスする
  - _Requirements: 1.2, 1.3, 5.1_

- [ ] 3. Core: 現在時刻取得とタイムゾーン変換
- [x] 3.1 (P) JST既定の現在時刻取得実装
  - タイムゾーン未指定時にJSTのawareな現在時刻を返す機能を実装する
  - タイムゾーンを明示的に指定した場合、そのタイムゾーンでの現在時刻を返す
  - タイムゾーン引数が文字列/`tzinfo`/`None` のいずれでもない場合、`TypeError` を送出する
  - Observable: 引数なし呼び出しの返り値の `tzinfo` がJSTと一致することを検証するユニットテストがパスする
  - _Requirements: 1.1, 1.2, 1.3, 5.2_
  - _Boundary: clock_

- [x] 3.2 (P) naive/aware変換とタイムゾーン間変換の実装
  - naiveなdatetimeにタイムゾーンを付与してawareにする変換(既定JST、`default_tz` 明示指定時はそれを優先)を実装する
  - awareなdatetimeをJST/UTC/任意タイムゾーンへ変換する関数を実装し、変換前後で絶対時刻(UTC換算値)を保持する
  - 変換対象が `datetime` 型でない(`None` を含む)場合、`TypeError` を送出する
  - Observable: naiveなdatetimeをUTC変換した結果がJST解釈を前提とした値と一致し、UTC変換後にJSTへ戻すラウンドトリップが元の値と一致することを検証するユニットテストがパスする
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 4.1, 4.2, 5.2_
  - _Boundary: convert_

- [ ] 4. Core: 日時のフォーマットとパース
- [x] 4.1 事前定義フォーマットでのフォーマット実装
  - 事前定義フォーマット識別子(ISO/DATE/DATETIME/JAPANESE_DATE/JAPANESE_DATETIME)を定義する
  - `locale` モジュールを使わず、固定の日本語曜日名テーブルを用いて曜日表記を含む文字列を生成する
  - フォーマット対象が `datetime` 型でない場合、`TypeError` を送出する
  - Observable: 各事前定義フォーマットについて、日本語曜日を含む出力が期待するパターンと一致することを検証するユニットテストがパスする
  - _Requirements: 3.1, 3.2, 5.2_
  - _Depends: 2_

- [x] 4.2 パースと優先順位付きフォーマット推定の実装
  - タイムゾーン情報を含まない日時文字列を指定タイムゾーン(既定JST)として解釈するパース機能を実装する
  - フォーマット未指定時はISO形式を最優先し、続けてDATETIME→DATE→JAPANESE_DATETIME→JAPANESE_DATEの順に解析を試行する
  - すべてのフォーマットで解析に失敗した場合、または指定フォーマットに文字列が一致しない場合、`DateTimeParseError` を送出する
  - Observable: `format_datetime` で生成した文字列を `parse_datetime` にフォーマット未指定のまま渡すと元のawareなdatetimeを復元できることを検証するユニットテストがパスする
  - _Requirements: 3.3, 3.4_
  - _Depends: 3.2, 4.1_

- [x] 5. 公開APIの集約
  - `now`, `to_jst`, `to_utc`, `to_timezone`, `format_datetime`, `parse_datetime`, `JST`, `DateTimeFormat`, `InvalidTimezoneError`, `DateTimeParseError` を `time_utility` パッケージのトップレベルから再エクスポートする
  - Observable: `from python_util.time_utility import now, to_jst, to_utc, to_timezone, format_datetime, parse_datetime, JST, DateTimeFormat, InvalidTimezoneError, DateTimeParseError` が全シンボルに対して成功する
  - _Requirements: 1.1, 1.2, 1.3, 2.1, 2.2, 2.3, 2.4, 3.1, 3.2, 3.3, 3.4, 4.1, 4.2, 5.1, 5.2_
  - _Depends: 2, 3.1, 3.2, 4.1, 4.2_

- [ ] 6. Validation: 結合検証とエラーハンドリング一貫性確認
- [x] 6.1 現在時刻取得からフォーマット・パースまでのラウンドトリップ検証
  - 公開APIの `now()` で取得した値を `format_datetime` でフォーマットし、`parse_datetime` で再度パースして元のawareな値と一致することを確認する
  - Observable: このラウンドトリップシナリオを検証する統合テストがパスする
  - _Requirements: 1.1, 1.2, 1.3, 3.1, 3.2, 3.3_
  - _Depends: 5_

- [x] 6.2 タイムゾーン変換ラウンドトリップとエラーハンドリング一貫性の検証
  - 公開APIの `to_utc` で変換した値を `to_jst` で戻した際に元の値と一致することを確認する
  - 不正なタイムゾーン名を `now`/`to_timezone`/`parse_datetime` それぞれに渡した際、一貫して `InvalidTimezoneError` が送出されることを確認する
  - Observable: ラウンドトリップ確認とエラーハンドリング一貫性確認の両方を含む統合テストがパスする
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 5.1_
  - _Depends: 5_
