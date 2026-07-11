"""バイナリデータおよびオブジェクトを文字列に可逆変換するコーデック。"""

from __future__ import annotations

from python_util.binary_string_codec.bytes_codec import decode_bytes, encode_bytes
from python_util.binary_string_codec.exceptions import BinaryStringDecodeError, ObjectPickleError
from python_util.binary_string_codec.object_codec import decode_object, encode_object

__all__ = [
    "BinaryStringDecodeError",
    "ObjectPickleError",
    "decode_bytes",
    "decode_object",
    "encode_bytes",
    "encode_object",
]
