"""compression モジュールのテスト。"""

from __future__ import annotations

import random
import zlib

from python_util.binary_string_codec.compression import compress_if_smaller


class TestCompressIfSmaller:
    def test_empty_payload_is_not_compressed(self) -> None:
        payload, compressed = compress_if_smaller(b"")
        assert payload == b""
        assert compressed is False

    def test_incompressible_random_data_falls_back_to_raw(self) -> None:
        random_payload = random.Random(0).randbytes(4096)
        payload, compressed = compress_if_smaller(random_payload)
        assert compressed is False
        assert payload == random_payload

    def test_highly_compressible_text_data_is_compressed(self) -> None:
        text_payload = b"hello world, " * 1000
        payload, compressed = compress_if_smaller(text_payload)
        assert compressed is True
        assert payload == zlib.compress(text_payload, level=9)
        assert len(payload) < len(text_payload)

    def test_compressed_result_never_larger_than_raw(self) -> None:
        random_payload = random.Random(0).randbytes(4096)
        for payload in [b"", b"x", b"hello world, " * 1000, random_payload]:
            result, _ = compress_if_smaller(payload)
            assert len(result) <= len(payload)
