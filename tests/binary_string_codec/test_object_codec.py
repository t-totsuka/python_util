"""object_codec モジュールのテスト。"""

from __future__ import annotations

import dataclasses

import pytest

from python_util.binary_string_codec.exceptions import ObjectPickleError
from python_util.binary_string_codec.object_codec import decode_object, encode_object


@dataclasses.dataclass
class _Point:
    x: int
    y: str


class _PlainRecord:
    def __init__(self, a: int, b: str) -> None:
        self.a = a
        self.b = b


def test_round_trip_dataclass_uses_eq() -> None:
    original = _Point(x=1, y="hello")
    decoded = decode_object(encode_object(original))
    assert decoded == original


def test_round_trip_plain_class_compares_attributes() -> None:
    original = _PlainRecord(a=42, b="value")
    decoded = decode_object(encode_object(original))
    assert type(decoded) is type(original)
    assert vars(decoded) == vars(original)


def test_encode_object_returns_str() -> None:
    encoded = encode_object(_Point(x=0, y=""))
    assert isinstance(encoded, str)


def test_decode_object_rejects_non_str() -> None:
    with pytest.raises(TypeError):
        decode_object(b"not str")  # type: ignore[arg-type]


def test_encode_object_rejects_unpicklable_object() -> None:
    def unpicklable() -> None:
        return None

    with pytest.raises(ObjectPickleError) as exc_info:
        encode_object(unpicklable)
    assert exc_info.value.__cause__ is not None
