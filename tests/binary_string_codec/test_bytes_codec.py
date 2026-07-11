"""bytes_codec モジュールのテスト。"""

from __future__ import annotations

import string

import pytest

from python_util.binary_string_codec.bytes_codec import decode_bytes, encode_bytes

_PRINTABLE_ASCII = set(string.printable) - set(string.whitespace) | {" "}


@pytest.mark.parametrize(
    "data",
    [
        b"",
        b"hello world",
        b"\x00\x01\x02\xff\xfe",
        b"a" * 1000,
        bytes(range(256)),
    ],
)
def test_単体正常系_encode_bytesとdecode_bytesが_任意のバイト列を受け取った場合_元のバイト列に復元する(
    data: bytes,
) -> None:
    assert decode_bytes(encode_bytes(data)) == data


def test_単体正常系_encode_bytesが_バイナリデータを受け取った場合_印字可能なASCII文字のみの文字列を返す() -> None:
    encoded = encode_bytes(b"\x00\x01\x02binary data\xff\xfe" * 10)
    assert set(encoded) <= _PRINTABLE_ASCII


def test_境界_encode_bytesが_空バイト列を受け取った場合_有効な文字列を返す() -> None:
    encoded = encode_bytes(b"")
    assert isinstance(encoded, str)
    assert decode_bytes(encoded) == b""


def test_異常系_encode_bytesが_bytes型以外を受け取った場合_TypeErrorを送出する() -> None:
    with pytest.raises(TypeError):
        encode_bytes("not bytes")  # type: ignore[arg-type]


def test_異常系_decode_bytesが_str型以外を受け取った場合_TypeErrorを送出する() -> None:
    with pytest.raises(TypeError):
        decode_bytes(b"not str")  # type: ignore[arg-type]
