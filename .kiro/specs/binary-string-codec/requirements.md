# Requirements Document

## Project Description (Input)
バイナリデータを高度に圧縮された文字列にエンコード・デコードを実施したい
- バイナリデータをJSON,TOMLなどに保存したいときに文字列の方が有利なことが多いので双方向に変換できるような機能が欲しい

## Introduction
本機能は、任意の `bytes` データを文字列（`str`）に変換し、また元の `bytes` に復元できる可逆的なコーデックを提供する。JSON や TOML のようなテキストベースの設定・データファイルにバイナリデータを埋め込む際、Base64 のような一般的なエンコードよりも高い情報密度で、かつ可能な限りエンコード後のサイズを抑えることを目的とする。`python_util` パッケージの新規サブパッケージとして提供し、既存の `logging` / `time_utility` サブパッケージと同様の設計規約（型ヒント必須、公開APIの `__init__.py` への集約、専用例外クラスなど）に従う。

## Boundary Context (Optional)

- **In scope**: 任意の `bytes` を文字列にエンコードする機能、その文字列を元の `bytes` に完全に復元するデコード機能、圧縮によるエンコード後サイズの削減、JSON/TOML に安全に埋め込める文字集合の保証、`pickle` 化可能な任意の Python オブジェクト（dataclass 等のデータモデルを含む）をバイナリ化・文字列化し元のオブジェクトへ復元する機能
- **Out of scope**: 暗号化・署名等のセキュリティ機能、ネットワーク経由でのシリアライズ/デシリアライズ、JSON/TOML ファイルそのものの読み書き機能（あくまで文字列⇔バイナリの変換のみを提供する）、信頼できない発信元の文字列を安全にデコードするためのサニタイズ・検証機構
- **Adjacent expectations**: 呼び出し側が生成された文字列を JSON の文字列値や TOML の基本文字列としてそのまま埋め込むこと、`logging`/`time_utility` と同様に `pyproject.toml` の `[tool.python_util.binary_string_codec]` によるオーバーライドは本機能では必須としない（必要になった場合は別途検討）。オブジェクトのデコード機能は内部的に `pickle` を利用するため任意コード実行のリスクを伴う。呼び出し側は自身が生成・保存した信頼できる文字列のみをデコード対象とし、外部から受け取った未検証の文字列をデコードしないことを前提とする

## Requirements

### Requirement 1: バイナリデータのエンコード

**Objective:** As a 開発者, I want `bytes` データをコンパクトな文字列に変換する機能, so that バイナリデータを JSON や TOML などのテキストベースのファイルに埋め込んで保存できる

#### Acceptance Criteria

1. When 開発者が `bytes` データをエンコード関数に渡す, the Binary String Codec shall その `bytes` を表す `str` 型の値を返す
2. The Binary String Codec shall エンコード結果の文字列を、JSON および TOML の文字列リテラルとして安全に埋め込める印字可能な ASCII 文字のみで構成する
3. When 空の `bytes`（`b""`）がエンコード関数に渡される, the Binary String Codec shall 空データを表す有効な文字列を返す
4. The Binary String Codec shall メモリが許す限り任意の長さの `bytes` データをエンコードできる

### Requirement 2: 文字列からのデコードと往復整合性

**Objective:** As a 開発者, I want エンコードされた文字列を元の `bytes` に完全に復元する機能, so that 保存したバイナリデータを損失なく再取得できる

#### Acceptance Criteria

1. When エンコード関数が生成した文字列がデコード関数に渡される, the Binary String Codec shall エンコード前の `bytes` と完全に一致する `bytes` を返す
2. The Binary String Codec shall 任意の `bytes` データ `data` に対して `decode(encode(data)) == data` を満たす
3. When 空文字列相当のエンコード結果（Requirement 1.3 で生成されたもの）がデコード関数に渡される, the Binary String Codec shall 空の `bytes`（`b""`）を返す

### Requirement 3: 高圧縮率のエンコーディング

**Objective:** As a 開発者, I want Base64 よりも情報密度が高く、かつ圧縮を活用したエンコーディング, so that JSON/TOML に保存する文字列のサイズをできるだけ小さく抑えられる

#### Acceptance Criteria

1. The Binary String Codec shall Base64 よりも1文字あたりの情報密度が高いエンコード方式（例: Base85 系）を採用する
2. Where 入力データが圧縮によってサイズを削減できる, the Binary String Codec shall エンコード前に圧縮処理を適用し、エンコード後の文字列長を削減する
3. If 圧縮を適用してもエンコード後のサイズが圧縮なしの場合より小さくならない, then the Binary String Codec shall 圧縮を適用せずに元データをエンコードする
4. The Binary String Codec shall エンコード後の文字列に、デコード時に圧縮の有無を判定できる情報を含める
5. The Binary String Codec shall 採用する圧縮アルゴリズムを、代表的なテストデータ（テキスト系バイナリ、繰り返しパターンを含むデータ、ランダムデータ等）に対して圧縮なしの Base64 エンコードとのサイズ比較を行った上で決定する
6. The Binary String Codec shall 圧縮効果が見込めるデータにおいて、圧縮なしの Base64 エンコードよりも短いエンコード結果を生成する

### Requirement 4: 入力検証とエラーハンドリング

**Objective:** As a 開発者, I want 不正な入力に対して明確なエラーが発生すること, so that デコード処理の失敗を早期に検知し、原因を特定できる

#### Acceptance Criteria

1. If エンコード関数に `bytes` 型ではない値が渡される, then the Binary String Codec shall `TypeError` を送出する
2. If デコード関数に `str` 型ではない値が渡される, then the Binary String Codec shall `TypeError` を送出する
3. If デコード関数に本コーデックが生成したものではない不正な形式の文字列が渡される, then the Binary String Codec shall 専用の例外クラスを送出する
4. If デコード対象の文字列が破損しており元の `bytes` を復元できない, then the Binary String Codec shall 専用の例外クラスを送出する

### Requirement 5: データモデルオブジェクトのバイナリ化

**Objective:** As a 開発者, I want dataclass 等のデータモデルを含む Python オブジェクトそのものを文字列にエンコード・デコードする機能, so that 生バイナリだけでなく構造化されたオブジェクトも JSON/TOML に保存し、復元できる

#### Acceptance Criteria

1. When 開発者が `pickle` 化可能な Python オブジェクトをオブジェクトエンコード関数に渡す, the Binary String Codec shall そのオブジェクトを `pickle` を用いてバイナリ化した上で、Requirement 1 のエンコード処理を適用した `str` 型の値を返す
2. When オブジェクトエンコード関数が生成した文字列がオブジェクトデコード関数に渡される, the Binary String Codec shall 元のオブジェクトと型および値が等価なオブジェクトを返す
3. If オブジェクトエンコード関数に渡されたオブジェクトが `pickle`化できない（オープンなファイルハンドルなど非対応の参照を含む）, then the Binary String Codec shall 専用の例外クラスを送出する
4. If オブジェクトデコード関数に渡された文字列が本コーデックのオブジェクトエンコード関数が生成したものではない、または破損している, then the Binary String Codec shall 専用の例外クラスを送出する
5. The Binary String Codec shall オブジェクトデコード関数の公開APIドキュメント（docstring）に、内部で `pickle.loads` 相当の処理を行うため信頼できない発信元の文字列をデコードすると任意コード実行のリスクがある旨を明記する

### Requirement 6: 公開APIとプロジェクト規約への準拠

**Objective:** As a `python_util` の利用者, I want 他のサブパッケージと一貫したインターフェースと品質基準, so that パッケージ全体を予測可能な方法で利用できる

#### Acceptance Criteria

1. The Binary String Codec shall `src/python_util/binary_string_codec/` サブパッケージとして提供され、公開APIを `__init__.py` の `__all__` に限定してエクスポートする（`bytes` のエンコード/デコード関数、オブジェクトのエンコード/デコード関数を含む）
2. The Binary String Codec shall 全モジュール冒頭で `from __future__ import annotations` を宣言し、公開関数に型ヒントと日本語の一行docstringを付与する
3. The Binary String Codec shall サブパッケージ固有の例外を `exceptions.py` に集約し、`ValueError` を継承するクラスとして定義する
4. The Binary String Codec shall `tests/binary_string_codec/` に `src/python_util/binary_string_codec/` の構成をミラーリングしたテストコードを持つ
