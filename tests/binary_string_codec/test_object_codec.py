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


def test_単体正常系_encode_objectとdecode_objectが_dataclassインスタンスを受け取った場合_eq比較で等しい値を復元する() -> None:
    original = _Point(x=1, y="hello")
    decoded = decode_object(encode_object(original))
    assert decoded == original


def test_単体正常系_encode_objectとdecode_objectが_通常クラスインスタンスを受け取った場合_型と属性値が一致する値を復元する() -> None:
    original = _PlainRecord(a=42, b="value")
    decoded = decode_object(encode_object(original))
    assert type(decoded) is type(original)
    assert vars(decoded) == vars(original)


def test_単体正常系_encode_objectが_オブジェクトを受け取った場合_str型を返す() -> None:
    encoded = encode_object(_Point(x=0, y=""))
    assert isinstance(encoded, str)


def test_異常系_decode_objectが_str型以外を受け取った場合_TypeErrorを送出する() -> None:
    with pytest.raises(TypeError):
        decode_object(b"not str")  # type: ignore[arg-type]


def test_異常系_encode_objectが_pickle不可能なオブジェクトを受け取った場合_ObjectPickleErrorを送出し元例外を保持する() -> None:
    def unpicklable() -> None:
        return None

    with pytest.raises(ObjectPickleError) as exc_info:
        encode_object(unpicklable)
    assert exc_info.value.__cause__ is not None
