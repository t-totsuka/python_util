# python_util

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

## 開発

```bash
pdm install
pdm run pytest
```
