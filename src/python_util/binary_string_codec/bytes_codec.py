"""bytesと文字列を相互変換するエンコード/デコード関数を提供する。"""

from __future__ import annotations

import base64
import zlib

from python_util.binary_string_codec.compression import compress_if_smaller
from python_util.binary_string_codec.envelope import _PayloadKind, pack, unpack
from python_util.binary_string_codec.exceptions import BinaryStringDecodeError


def encode_bytes(data: bytes) -> str:
    """bytesをJSON/TOMLに安全に埋め込める印字可能ASCII文字列に変換する。"""
    if not isinstance(data, bytes):
        raise TypeError(f"dataはbytes型である必要があります: {data!r}")
    payload, compressed = compress_if_smaller(data)
    envelope = pack(payload, compressed=compressed, kind=_PayloadKind.BYTES)
    return base64.b85encode(envelope).decode("ascii")


def decode_bytes(text: str) -> bytes:
    """encode_bytesが生成した文字列を元のbytesに復元する。"""
    if not isinstance(text, str):
        raise TypeError(f"textはstr型である必要があります: {text!r}")
    try:
        envelope = base64.b85decode(text)
    except ValueError as exc:
        raise BinaryStringDecodeError(text) from exc
    payload, compressed = unpack(envelope, expected_kind=_PayloadKind.BYTES)
    if compressed:
        return zlib.decompress(payload)
    return payload
