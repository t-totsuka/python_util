"""compression モジュールのテスト。"""

from __future__ import annotations

import random
import zlib

from python_util.binary_string_codec.compression import compress_if_smaller


class TestCompressIfSmaller:
    def test_境界_compress_if_smallerが_空データを受け取った場合_圧縮せずそのまま返す(self) -> None:
        payload, compressed = compress_if_smaller(b"")
        assert payload == b""
        assert compressed is False

    def test_単体正常系_compress_if_smallerが_非圧縮性のランダムデータを受け取った場合_元データのまま返す(
        self,
    ) -> None:
        random_payload = random.Random(0).randbytes(4096)
        payload, compressed = compress_if_smaller(random_payload)
        assert compressed is False
        assert payload == random_payload

    def test_単体正常系_compress_if_smallerが_高圧縮率のテキストデータを受け取った場合_圧縮済みデータを返す(
        self,
    ) -> None:
        text_payload = b"hello world, " * 1000
        payload, compressed = compress_if_smaller(text_payload)
        assert compressed is True
        assert payload == zlib.compress(text_payload, level=9)
        assert len(payload) < len(text_payload)

    def test_単体正常系_compress_if_smallerが_任意のデータを受け取った場合_圧縮結果が元データ長を超えない(
        self,
    ) -> None:
        random_payload = random.Random(0).randbytes(4096)
        for payload in [b"", b"x", b"hello world, " * 1000, random_payload]:
            result, _ = compress_if_smaller(payload)
            assert len(result) <= len(payload)
