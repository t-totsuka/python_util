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

## 開発

```bash
pdm install
pdm run pytest
```
