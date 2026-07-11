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
    def test_text_repeat_sample_is_smaller_than_base64(self) -> None:
        encoded = encode_bytes(_TEXT_REPEAT_SAMPLE)
        assert len(encoded) < _base64_length(_TEXT_REPEAT_SAMPLE)

    def test_prose_sample_is_smaller_than_base64(self) -> None:
        encoded = encode_bytes(_PROSE_SAMPLE)
        assert len(encoded) < _base64_length(_PROSE_SAMPLE)


class TestIncompressibleDataFallsBackToRawBase85Size:
    def test_random_data_stays_at_uncompressed_base85_size(self) -> None:
        random_payload = random.Random(42).randbytes(2000)
        encoded = encode_bytes(random_payload)
        expected_length = len(
            base64.b85encode(b"\x00\x00\x00\x00" + random_payload).decode("ascii")
        )
        assert len(encoded) == expected_length
