"""エンコード対象ペイロードのヘッダ（magic/version/flags）のpack/unpackを担う。"""

from __future__ import annotations

import enum

from python_util.binary_string_codec.exceptions import BinaryStringDecodeError

_MAGIC = b"BS"
_VERSION = 0x01
_FLAG_COMPRESSED = 0b0000_0001
_FLAG_KIND = 0b0000_0010
_FLAG_RESERVED_MASK = 0b1111_1100
_HEADER_LENGTH = 4


class _PayloadKind(enum.IntEnum):
    """envelopeが表すペイロードの種別。"""

    BYTES = 0
    OBJECT = 1


def pack(payload: bytes, *, compressed: bool, kind: _PayloadKind) -> bytes:
    """ペイロードにmagic/version/flagsからなる固定ヘッダを付与したバイト列を返す。"""
    flags = 0
    if compressed:
        flags |= _FLAG_COMPRESSED
    if kind is _PayloadKind.OBJECT:
        flags |= _FLAG_KIND
    header = _MAGIC + bytes([_VERSION, flags])
    return header + payload


def unpack(data: bytes, *, expected_kind: _PayloadKind) -> tuple[bytes, bool]:
    """ヘッダを検証しつつペイロード本体と圧縮フラグを復元する。"""
    if len(data) < _HEADER_LENGTH or data[0:2] != _MAGIC:
        raise BinaryStringDecodeError(data)
    if data[2] != _VERSION:
        raise BinaryStringDecodeError(data)
    flags = data[3]
    if flags & _FLAG_RESERVED_MASK:
        raise BinaryStringDecodeError(data)
    kind = _PayloadKind.OBJECT if flags & _FLAG_KIND else _PayloadKind.BYTES
    if kind is not expected_kind:
        raise BinaryStringDecodeError(data)
    compressed = bool(flags & _FLAG_COMPRESSED)
    return data[_HEADER_LENGTH:], compressed
