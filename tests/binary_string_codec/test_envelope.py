"""envelope モジュールのテスト。"""

from __future__ import annotations

import pytest

from python_util.binary_string_codec.envelope import _PayloadKind, pack, unpack
from python_util.binary_string_codec.exceptions import BinaryStringDecodeError


class TestPackUnpackRoundTrip:
    @pytest.mark.parametrize("payload", [b"", b"hello world", bytes(range(256))])
    @pytest.mark.parametrize("compressed", [True, False])
    @pytest.mark.parametrize("kind", [_PayloadKind.BYTES, _PayloadKind.OBJECT])
    def test_round_trip(
        self, payload: bytes, compressed: bool, kind: _PayloadKind
    ) -> None:
        packed = pack(payload, compressed=compressed, kind=kind)
        unpacked_payload, unpacked_compressed = unpack(packed, expected_kind=kind)
        assert unpacked_payload == payload
        assert unpacked_compressed == compressed

    def test_pack_returns_at_least_header_length(self) -> None:
        packed = pack(b"", compressed=False, kind=_PayloadKind.BYTES)
        assert len(packed) >= 4


class TestUnpackInvalidData:
    def _valid_packed(self) -> bytearray:
        return bytearray(
            pack(b"payload", compressed=False, kind=_PayloadKind.BYTES)
        )

    def test_raises_on_magic_mismatch(self) -> None:
        data = self._valid_packed()
        data[0:2] = b"XX"
        with pytest.raises(BinaryStringDecodeError):
            unpack(bytes(data), expected_kind=_PayloadKind.BYTES)

    def test_raises_on_version_mismatch(self) -> None:
        data = self._valid_packed()
        data[2] = 0xFF
        with pytest.raises(BinaryStringDecodeError):
            unpack(bytes(data), expected_kind=_PayloadKind.BYTES)

    def test_raises_on_reserved_flag_bits_nonzero(self) -> None:
        data = self._valid_packed()
        data[3] |= 0b1000_0000
        with pytest.raises(BinaryStringDecodeError):
            unpack(bytes(data), expected_kind=_PayloadKind.BYTES)

    def test_raises_on_payload_kind_mismatch(self) -> None:
        packed = pack(b"payload", compressed=False, kind=_PayloadKind.BYTES)
        with pytest.raises(BinaryStringDecodeError):
            unpack(packed, expected_kind=_PayloadKind.OBJECT)
