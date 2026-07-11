"""zlibによる圧縮要否判定を担う。"""

from __future__ import annotations

import zlib

_COMPRESSION_LEVEL = 9


def compress_if_smaller(payload: bytes) -> tuple[bytes, bool]:
    """zlib圧縮した結果が元データより小さい場合のみ圧縮済みペイロードを返す。"""
    compressed = zlib.compress(payload, level=_COMPRESSION_LEVEL)
    if len(compressed) < len(payload):
        return compressed, True
    return payload, False
