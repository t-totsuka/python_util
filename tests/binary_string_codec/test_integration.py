"""デコード時の種別不一致・破損データ検出に関する統合テスト。"""

from __future__ import annotations

import base64

import pytest

from python_util.binary_string_codec.bytes_codec import decode_bytes, encode_bytes
from python_util.binary_string_codec.exceptions import BinaryStringDecodeError
from python_util.binary_string_codec.object_codec import decode_object, encode_object


def test_結合_decode_bytesが_encode_objectの出力を受け取った場合_BinaryStringDecodeErrorを送出する() -> None:
    with pytest.raises(BinaryStringDecodeError):
        decode_bytes(encode_object({"a": 1}))


def test_結合_decode_objectが_encode_bytesの出力を受け取った場合_BinaryStringDecodeErrorを送出する() -> None:
    with pytest.raises(BinaryStringDecodeError):
        decode_object(encode_bytes(b"hello"))


def test_異常系_decode_bytesが_base85として不正な文字列を受け取った場合_BinaryStringDecodeErrorを送出する() -> None:
    with pytest.raises(BinaryStringDecodeError):
        decode_bytes("not valid base85 !!!")


def test_異常系_decode_objectが_base85として不正な文字列を受け取った場合_BinaryStringDecodeErrorを送出する() -> None:
    with pytest.raises(BinaryStringDecodeError):
        decode_object("not valid base85 !!!")


def test_異常系_decode_bytesが_ヘッダーが欠損した切り詰めデータを受け取った場合_BinaryStringDecodeErrorを送出する() -> None:
    raw = base64.b85decode(encode_bytes(b"hello world"))
    truncated = base64.b85encode(raw[:2]).decode("ascii")
    with pytest.raises(BinaryStringDecodeError):
        decode_bytes(truncated)


def test_異常系_decode_objectが_ヘッダーが欠損した切り詰めデータを受け取った場合_BinaryStringDecodeErrorを送出する() -> None:
    raw = base64.b85decode(encode_object({"a": 1}))
    truncated = base64.b85encode(raw[:2]).decode("ascii")
    with pytest.raises(BinaryStringDecodeError):
        decode_object(truncated)
