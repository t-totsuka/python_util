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
def test_round_trip(data: bytes) -> None:
    assert decode_bytes(encode_bytes(data)) == data


def test_encode_bytes_returns_printable_ascii_only() -> None:
    encoded = encode_bytes(b"\x00\x01\x02binary data\xff\xfe" * 10)
    assert set(encoded) <= _PRINTABLE_ASCII


def test_encode_empty_bytes_returns_valid_string() -> None:
    encoded = encode_bytes(b"")
    assert isinstance(encoded, str)
    assert decode_bytes(encoded) == b""


def test_encode_bytes_rejects_non_bytes() -> None:
    with pytest.raises(TypeError):
        encode_bytes("not bytes")  # type: ignore[arg-type]


def test_decode_bytes_rejects_non_str() -> None:
    with pytest.raises(TypeError):
        decode_bytes(b"not str")  # type: ignore[arg-type]
