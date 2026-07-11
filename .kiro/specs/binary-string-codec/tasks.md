# Implementation Plan

- [ ] 1. Foundation: サブパッケージの雛形とテスト基盤、共有例外の整備
- [x] 1.1 サブパッケージとテストディレクトリの雛形作成
  - `src/python_util/binary_string_codec/` 配下に `envelope`, `compression`, `bytes_codec`, `object_codec`, `__init__` の空モジュールを作成し、パッケージとしてimport可能な状態にする
  - `tests/binary_string_codec/` 配下に `test_envelope.py`, `test_compression.py`, `test_bytes_codec.py`, `test_object_codec.py`, `test_exceptions.py`, `test_public_api.py` の雛形と `__init__.py` を作成する
  - Observable: `import python_util.binary_string_codec` がエラーなく成功し、`pytest tests/binary_string_codec/` がテスト0件でエラーなく完了する
  - _Requirements: 6.1, 6.4_

- [x] 1.2 例外クラスの定義とユニットテスト
  - `exceptions.py` に `BinaryStringDecodeError` と `ObjectPickleError` を `ValueError` 継承で定義し、`time_utility.exceptions` と同様に不正値を `f"...: {value!r}"` 形式で日本語メッセージ化する
  - 各例外クラスが `ValueError` のサブクラスであり、渡した値がメッセージに含まれることを `test_exceptions.py` で検証する
  - Observable: `pytest tests/binary_string_codec/test_exceptions.py` の全テストがパスする
  - _Requirements: 4.3, 4.4, 5.3, 5.4, 6.2, 6.3_

- [ ] 2. Core: 基盤コーデック機能（envelope/compression）の実装
- [x] 2.1 (P) envelopeのヘッダpack/unpack実装
  - マジックバイト・バージョン・フラグ（圧縮有無／ペイロード種別）からなる固定ヘッダと可変長ペイロードをpack/unpackする関数、および `_PayloadKind`（BYTES/OBJECT）を実装する
  - マジックバイト不一致・バージョン不一致・フラグ予約ビット非ゼロ・呼び出し元が期待するペイロード種別との不一致のいずれかを検出した場合に `BinaryStringDecodeError` を送出する
  - pack済みバイト列をunpackすると、元のペイロード・圧縮フラグ・ペイロード種別が完全に復元されることを `test_envelope.py` で検証する
  - Observable: pack→unpackの往復整合性テストと4種の異常系検出テストが `test_envelope.py` ですべてパスする
  - _Requirements: 3.4, 4.3, 4.4, 6.2_
  - _Boundary: envelope_

- [x] 2.2 (P) compressionのzlib圧縮要否判定実装
  - zlib（圧縮レベル9）で圧縮した結果の生バイト長が無圧縮の生バイト長より小さい場合のみ圧縮済みペイロードと圧縮フラグ`True`を返し、そうでない場合は元データとフラグ`False`を返す関数を実装する
  - 空バイト列・非圧縮性データ（ランダムバイト列）・圧縮効果の高いテキスト系データのそれぞれで正しい選択（圧縮採用/フォールバック）が行われることを `test_compression.py` で検証する
  - Observable: 圧縮が有効なケースと無効なケースの双方を含む `test_compression.py` の全テストがパスする
  - _Requirements: 3.2, 3.3, 3.5, 3.6, 6.2_
  - _Boundary: compression_

- [ ] 3. Core: bytesおよびオブジェクトコーデックの実装
- [x] 3.1 (P) bytes_codecのencode_bytes/decode_bytes実装
  - `encode_bytes` は `bytes` 型以外の入力で `TypeError` を送出し、`compression` による圧縮要否判定と `envelope` によるヘッダ付与を経て、Base85エンコードした `str` を返す
  - `decode_bytes` は `str` 型以外の入力で `TypeError` を送出し、Base85デコード後に `envelope` でペイロード種別が `BYTES` であることを検証した上で元の `bytes` を復元する
  - 空バイト列を含む任意の `bytes` について `decode_bytes(encode_bytes(data)) == data` が成立し、エンコード結果が印字可能ASCII文字のみで構成されることを `test_bytes_codec.py` で検証する
  - Observable: 空バイト列を含む往復整合性テストと型不正時の `TypeError` 送出テストが `test_bytes_codec.py` ですべてパスする
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 2.1, 2.2, 2.3, 3.1, 4.1, 6.2_
  - _Boundary: bytes_codec_

- [x] 3.2 (P) object_codecのencode_object/decode_object実装
  - `encode_object` は `pickle.dumps(obj, protocol=pickle.HIGHEST_PROTOCOL)` の結果を `bytes_codec` と共通の `compression`/`envelope` 処理に渡してBase85文字列を返し、pickle化に失敗した場合は元例外を `__cause__` に保持した `ObjectPickleError` を送出する
  - `decode_object` は `str` 型以外の入力で `TypeError` を送出し、`envelope` でペイロード種別が `OBJECT` であることを検証した上で `pickle.loads` によりオブジェクトを復元し、失敗時は `BinaryStringDecodeError` を送出する
  - `decode_object` の公開APIドキュメント（docstring）に、信頼できない発信元の文字列をデコードすると任意コード実行のリスクがある旨を明記する
  - `__eq__` が自動生成されるdataclassインスタンスでの `==` による往復整合性、および `__eq__` を独自定義していないプレーンなクラスでの属性値（`vars()`）レベルの往復整合性を `test_object_codec.py` で検証する
  - Observable: pickle化不可オブジェクトでの `ObjectPickleError` 送出を含む `test_object_codec.py` の全テストがパスする
  - _Requirements: 4.2, 5.1, 5.2, 5.3, 5.4, 5.5, 6.2_
  - _Boundary: object_codec_

- [x] 4. Integration: 公開APIの集約とエクスポート検証
  - `encode_bytes`, `decode_bytes`, `encode_object`, `decode_object`, `BinaryStringDecodeError`, `ObjectPickleError` を `__init__.py` の `__all__` にアルファベット順で列挙してエクスポートし、`envelope`/`compression`/`_PayloadKind` 等の内部シンボルは非公開のままとする
  - `test_public_api.py` で全公開シンボルが `python_util.binary_string_codec` から直接インポート可能であることと、bytes・オブジェクトそれぞれの往復動作を検証する
  - Observable: `from python_util.binary_string_codec import encode_bytes, decode_bytes, encode_object, decode_object, BinaryStringDecodeError, ObjectPickleError` が成功し、`test_public_api.py` がパスする
  - _Requirements: 6.1, 6.2, 6.4_
  - _Depends: 3.1, 3.2_

- [ ] 5. Validation: 異常系の統合検証と圧縮効果の回帰テスト
- [x] 5.1 (P) デコード時の種別不一致・破損データ検出の統合テスト
  - `decode_bytes` に `encode_object` の出力を渡した場合、および `decode_object` に `encode_bytes` の出力を渡した場合の双方で `BinaryStringDecodeError` が送出されることを検証する
  - Base85デコード不能な文字列、およびenvelopeヘッダが途中で切断された文字列を `decode_bytes`/`decode_object` に渡した場合に `BinaryStringDecodeError` が送出されることを検証する
  - Observable: 種別不一致・破損データそれぞれの異常系統合テストがすべてパスする
  - _Requirements: 4.3, 4.4, 5.4_
  - _Depends: 3.1, 3.2_
  - _Boundary: bytes_codec, object_codec, envelope_

- [x] 5.2 (P) 圧縮効果のベンチマーク回帰テスト
  - [research.md](research.md) で実測したテキスト系・繰り返しパターンのサンプルデータについて、`encode_bytes` の出力長が同一データの単純Base64エンコード長より短いことを自動テストで検証する
  - ランダムデータについて圧縮フォールバックが機能し、無圧縮Base85エンコード相当のサイズに収まることを検証する
  - Observable: 圧縮効果データセットでのBase64比較回帰テストがすべてパスする
  - _Requirements: 3.6_
  - _Depends: 3.1_
  - _Boundary: bytes_codec, compression_

- [x] 6. README.mdの更新
  - README.mdに `binary_string_codec` サブパッケージの概要と、`encode_bytes`/`decode_bytes`/`encode_object`/`decode_object` の使用例を追記する
  - Observable: README.mdに `binary_string_codec` の説明と使用例セクションが追加されている
  - _Requirements: 6.1_
  - _Depends: 4_
