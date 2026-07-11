"""デコード時の種別不一致・破損データ検出に関する統合テスト。"""

from __future__ import annotations

import base64

import pytest

from python_util.binary_string_codec.bytes_codec import decode_bytes, encode_bytes
from python_util.binary_string_codec.exceptions import BinaryStringDecodeError
from python_util.binary_string_codec.object_codec import decode_object, encode_object


def test_decode_bytes_rejects_encode_object_output() -> None:
    with pytest.raises(BinaryStringDecodeError):
        decode_bytes(encode_object({"a": 1}))


def test_decode_object_rejects_encode_bytes_output() -> None:
    with pytest.raises(BinaryStringDecodeError):
        decode_object(encode_bytes(b"hello"))


def test_decode_bytes_rejects_undecodable_base85_string() -> None:
    with pytest.raises(BinaryStringDecodeError):
        decode_bytes("not valid base85 !!!")


def test_decode_object_rejects_undecodable_base85_string() -> None:
    with pytest.raises(BinaryStringDecodeError):
        decode_object("not valid base85 !!!")


def test_decode_bytes_rejects_truncated_envelope_header() -> None:
    raw = base64.b85decode(encode_bytes(b"hello world"))
    truncated = base64.b85encode(raw[:2]).decode("ascii")
    with pytest.raises(BinaryStringDecodeError):
        decode_bytes(truncated)


def test_decode_object_rejects_truncated_envelope_header() -> None:
    raw = base64.b85decode(encode_object({"a": 1}))
    truncated = base64.b85encode(raw[:2]).decode("ascii")
    with pytest.raises(BinaryStringDecodeError):
        decode_object(truncated)
