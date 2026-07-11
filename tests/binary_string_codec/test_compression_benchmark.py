"""圧縮効果のベンチマーク回帰テスト（research.mdのサンプルデータ種別に基づく）。"""

from __future__ import annotations

import base64
import random

from python_util.binary_string_codec.bytes_codec import encode_bytes

_TEXT_REPEAT_SAMPLE = b'{"name": "sample", "value": 123, "tags": ["a", "b", "c"]}' * 20
_PROSE_SAMPLE = ("これはテスト用の日本語の文章です。圧縮効果を確認するためのサンプルデータです。" * 60).encode("utf-8")


def _base64_length(data: bytes) -> int:
    return len(base64.b64encode(data).decode("ascii"))


class TestCompressibleDataBeatsBase64:
    def test_結合_encode_bytesが_繰り返しテキストデータを受け取った場合_base64エンコードよりも短い文字列を返す(
        self,
    ) -> None:
        encoded = encode_bytes(_TEXT_REPEAT_SAMPLE)
        assert len(encoded) < _base64_length(_TEXT_REPEAT_SAMPLE)

    def test_結合_encode_bytesが_日本語文章データを受け取った場合_base64エンコードよりも短い文字列を返す(
        self,
    ) -> None:
        encoded = encode_bytes(_PROSE_SAMPLE)
        assert len(encoded) < _base64_length(_PROSE_SAMPLE)


class TestIncompressibleDataFallsBackToRawBase85Size:
    def test_結合_encode_bytesが_非圧縮性のランダムデータを受け取った場合_非圧縮時のbase85サイズと一致する(
        self,
    ) -> None:
        random_payload = random.Random(42).randbytes(2000)
        encoded = encode_bytes(random_payload)
        expected_length = len(
            base64.b85encode(b"\x00\x00\x00\x00" + random_payload).decode("ascii")
        )
        assert len(encoded) == expected_length
