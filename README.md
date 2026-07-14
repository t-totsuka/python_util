# python_util

[![codecov](https://codecov.io/gh/t-totsuka/python_util/graph/badge.svg)](https://codecov.io/gh/t-totsuka/python_util)

個人用の Python ユーティリティ集。特定のドメインに限定せず、日常的な開発作業を下支えする汎用的なヘルパー関数・スクリプトを蓄積していくライブラリです。

## インストール

pdm を使う場合:

```bash
pdm add git+https://github.com/t-totsuka/python_util.git
```

pip を使う場合:

```bash
pip install git+https://github.com/t-totsuka/python_util.git
```

## 使い方

### logging: rich をラップしたロギングユーティリティ

`get_logger` を呼び出すだけで、rich による整形済みのコンソール出力が得られます。

```python
from python_util.logging import get_logger

logger = get_logger(__name__)
logger.info("Hello, world!")
```

- `get_logger()` を名前を省略して呼び出すと、呼び出し元のモジュール名がロガー名として使われます。
- 同じ名前で複数回呼び出しても、ハンドラが重複登録されることなく同一の設定を持つロガーが返されます。

#### pyproject.toml による設定

呼び出し側プロジェクトの `pyproject.toml` に `[tool.python_util.logging]` を記述すると、コードを変更せずにログの出力先・ログレベルを制御できます。

```toml
[tool.python_util.logging]
level = "INFO"        # 既定のログレベル（DEBUG/INFO/WARNING/ERROR/CRITICAL）
file = "logs/app.log" # ログファイルの出力先（省略時はファイル出力なし）
file_level = "DEBUG"  # ファイル出力専用のログレベル（省略時は level を継承）

[tool.python_util.logging.console]
enabled = true         # コンソール出力の有効/無効（既定: true）
level = "WARNING"      # コンソール出力専用のログレベル（省略時は level を継承）

# モジュール/クラス単位で出力先を個別に上書きする場合
[tool.python_util.logging.loggers."myapp.worker"]
file = "logs/worker.log"
level = "DEBUG"
```

- `[tool.python_util.logging]` を記述しない場合は、デフォルト設定（コンソール出力のみ、レベル `INFO`）で動作します。
- 設定ファイルの構文エラーや不正なログレベル指定があっても例外は発生せず、警告を出したうえでデフォルト設定にフォールバックします。
- `pyproject.toml` はカレントディレクトリから親方向へ探索され、最初に見つかったファイルが採用されます。

#### ログローテーション

> **挙動変更**: 本バージョンより、ファイル出力には日次のログローテーションが**既定で有効**になります。既存プロジェクトは設定変更なしにアップデートするだけで、更新後の初回書き込み時から前日以前のログが退避ファイルへ移り、保持期間（既定7日間）を超えた退避ファイルが自動削除されるようになります。

- ローテーションはローカル時刻の深夜0時を境界に日次で行われ、直前の書き込みから日付が変わった後の最初の書き込み時にまとめて退避されます。
- 当日のログは設定した出力先ファイル名のまま（例: `app.log`）書き出され、日付が変わったログは `{ファイル名の先頭部分}-{YYYY-MM-DD}.log`（例: `app-2026-07-13.log`、日付は退避対象ログが記録された日）という名前の退避ファイルへ移されます。
- 退避ファイルの既定の保持期間は7日間です。保持期間を超えた退避ファイルは自動的に削除されます。

`[tool.python_util.logging.rotation]` テーブルで、ローテーションの有効/無効と保持日数を制御できます。

```toml
[tool.python_util.logging.rotation]
enabled = true        # ローテーションの有効/無効（既定: true）
retention_days = 7     # 退避ファイルの保持日数（正の整数、既定: 7）
```

- ローテーションが不要な場合は `rotation.enabled = false` を設定すると、従来どおり単一のログファイルへ追記し続ける動作に戻せます。
- `retention_days` に0以下の値・真偽値・非整数など、`enabled` に真偽値以外の値など、不正な値が指定された場合も例外は発生せず、警告を出したうえで既定のローテーション設定（有効・保持7日間）にフォールバックします。

### time_utility: JSTを既定とした時刻ユーティリティ

`datetime` / `zoneinfo` を直接扱う際のタイムゾーン指定漏れや `locale` 設定の煩雑さを避け、特に指定がない限りJST(Asia/Tokyo)を前提に現在時刻取得・タイムゾーン変換・日時のフォーマット/パースを行えます。

```python
from python_util.time_utility import DateTimeFormat, format_datetime, now, parse_datetime, to_utc

jst_now = now()  # JSTのawareなdatetime
utc_now = to_utc(jst_now)  # UTCへ変換

text = format_datetime(jst_now, DateTimeFormat.JAPANESE_DATETIME)  # 例: "2026年07月11日(土) 09:00:00"
parsed = parse_datetime(text)  # フォーマット未指定でも自動判定してパース
```

- `now(tz=None)` はタイムゾーン未指定時にJSTのawareな `datetime` を返します。文字列(IANAタイムゾーン名)や `tzinfo` を渡すと、そのタイムゾーンでの現在時刻を返します。
- `to_jst()` / `to_utc()` / `to_timezone()` は、naiveな `datetime` を渡すとJSTとして解釈したうえで変換します。awareな `datetime` は元の絶対時刻を保ったまま変換されます。
- `format_datetime()` は `locale.setlocale` を使わず、固定の日本語曜日名テーブルで `DateTimeFormat.JAPANESE_DATE` / `JAPANESE_DATETIME` などの日本語表記を生成します。
- `parse_datetime()` はフォーマット未指定の場合、ISO形式を最優先に事前定義フォーマットを順に試行します。タイムゾーン情報を含まない文字列はJSTとして解釈されます。
- 不正なタイムゾーン名は `InvalidTimezoneError`、パースに失敗した文字列は `DateTimeParseError` を送出します(いずれも `ValueError` のサブクラス)。
- Windows環境では `zoneinfo` が利用するタイムゾーンDBの補完として `tzdata` パッケージが自動的にインストールされます。

### binary_string_codec: バイナリデータ・オブジェクトの文字列コーデック

任意の `bytes` および pickle 化可能な任意の Python オブジェクト（dataclass 等）を、JSON/TOML に安全に埋め込める文字列へ可逆変換します。Base85 エンコードと zlib 圧縮（効果がある場合のみ採用）により、単純な Base64 エンコードよりコンパクトな文字列を生成します。

```python
from python_util.binary_string_codec import decode_bytes, decode_object, encode_bytes, encode_object

# bytes ⇔ str
text = encode_bytes(b"hello world")
data = decode_bytes(text)
assert data == b"hello world"

# 任意のPythonオブジェクト ⇔ str
from dataclasses import dataclass

@dataclass
class Config:
    name: str
    value: int

obj_text = encode_object(Config(name="threshold", value=42))
restored = decode_object(obj_text)
assert restored == Config(name="threshold", value=42)
```

- エンコード結果は印字可能ASCII文字のみで構成され、JSON/TOMLの文字列リテラルにそのまま埋め込めます。
- 本コーデックが生成したものではない文字列や破損した文字列をデコードすると `BinaryStringDecodeError` を、pickle化できないオブジェクトを `encode_object` に渡すと `ObjectPickleError` を送出します（いずれも `ValueError` のサブクラス）。
- `decode_object` は内部で `pickle.loads` 相当の処理を行うため、信頼できない発信元の文字列をデコードすると任意コード実行のリスクがあります。自身が `encode_object` で生成した信頼できる文字列のみをデコード対象としてください。

### progress_display: richをラップした複数タスク進捗表示ユーティリティ

`ProgressDisplay` はコンテキストマネージャとして使うことで、複数タスクの進捗を単一のコンソール表示領域にまとめて表示できます。

```python
from python_util.progress_display import ProgressDisplay

with ProgressDisplay() as display:
    download_task = display.add_task("ダウンロード", total=100.0)
    convert_task = display.add_task("変換", total=50.0)

    display.update(download_task, advance=10.0)   # 相対増分で進捗を更新
    display.update(convert_task, completed=25.0)  # 絶対値で進捗を更新
```

イテラブルを処理しながら進捗を自動更新したい場合は `track()` を使います。

```python
from python_util.progress_display import ProgressDisplay

with ProgressDisplay() as display:
    for item in display.track(range(100), description="処理中"):
        ...  # item を処理
```

- `add_task()` は一意な `TaskID` を返し、`total` に0以下の値を指定すると `InvalidTotalError` を送出します。
- `update()` / `remove_task()` / `track()` に未知の `TaskID` を渡すと `UnknownTaskError` を送出します。
- `with` ブロックの外側（未開始状態）でタスク操作を行うと `DisplayNotStartedError` を送出します（いずれも `ValueError` のサブクラス）。

#### pyproject.toml による設定 (progress_display)

呼び出し側プロジェクトの `pyproject.toml` に `[tool.python_util.progress_display]` を記述すると、完了タスクの自動非表示や表示更新頻度を制御できます。

```toml
[tool.python_util.progress_display]
auto_remove_finished = true   # 完了したタスクを表示から自動的に取り除く（既定: false）
refresh_per_second = 5.0      # 表示の更新頻度（既定: 10.0）
```

- `[tool.python_util.progress_display]` を記述しない場合は、デフォルト設定（自動非表示なし、更新頻度10回/秒）で動作します。
- 設定ファイルの構文エラーや不正な値があっても例外は発生せず、警告を出したうえでデフォルト設定にフォールバックします。

## テストメソッド命名規則

テストコード自体が仕様書として機能するよう、テストメソッド名は日本語で記述します。以下の基本パターンをアンダースコア区切りで記述してください。

```text
test_(テスト目的)_(テスト対象)が_(状態)だった場合_(想定される結果)
```

- **テスト目的**: `単体正常系` / `異常系` / `境界` / `結合` など、テストの分類を表します
- **テスト対象**: 検証対象の関数・メソッド・クラスなど
- **状態**: テスト対象に与える入力や前提条件
- **想定される結果**: テスト対象から期待される出力・振る舞い

例:

```python
def test_単体正常系_残高照会APIが_有効なユーザーIDを受け取った場合_残高を返す():
    ...
```

- pytestの `test_` プレフィックスによるテスト収集規約と互換性を保つため、識別子は全角記号・空白を避け、区切りにはアンダースコアのみを用いてください（Pythonの構文上有効な識別子である必要があります）
- 上記は最低限の構成です。テストの意図を明確にするために必要であれば要素を追加しても構いません
- 本命名規則は今後 `.kiro/steering/` のプロジェクト全体ルールとして別途反映される予定です

## テストエビデンスの生成

`pdm run pytest` を実行するだけで、追加のコマンドオプションや設定変更なしに以下の2種類のテストエビデンスが自動生成されます。

```bash
pdm install
pdm run pytest
```

- `reports/test-evidence.md`: テスト結果のMarkdownレポート。サブパッケージ単位でグルーピングされた各テストケースの結果、合計/成功/失敗/スキップ件数、実行開始・終了時刻、失敗ケースの詳細を含みます。Gitで追跡され、コミットに含めることでテスト実施の証跡として残ります。
- `reports/coverage_html/index.html`: `pytest-cov` によるHTML形式のカバレッジレポート。`src/python_util` 配下のサブパッケージ・モジュール別に行カバレッジを確認できます。ブラウザで開いて閲覧してください。`reports/coverage_html/` は `.gitignore` により追跡対象外です。

### pre-commitによるコミット前フルスイート強制

コミットに含まれる `reports/test-evidence.md` が常にフィルタなしのフルスイート実行結果であることを保証するため、pre-commitフックを導入しています。初回のみ以下のコマンドでGitフックとして有効化してください。

```bash
pdm run pre-commit install
```

- 有効化後は `git commit` のたびにフィルタなしの `pdm run pytest` が自動実行されます。
- 全テストが成功した場合のみ、最新の `reports/test-evidence.md` が自動的にステージ（`git add`）されコミットに含まれます。
- いずれかのテストが失敗した場合はフックが非0で終了し、コミットがブロックされます。

## 開発

```bash
pdm install
pdm run pytest
```
