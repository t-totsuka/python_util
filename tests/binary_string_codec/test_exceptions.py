"""exceptions モジュールのテスト。"""

from __future__ import annotations

import pytest

from python_util.binary_string_codec.exceptions import (
    BinaryStringDecodeError,
    ObjectPickleError,
)


class TestBinaryStringDecodeError:
    def test_単体正常系_BinaryStringDecodeErrorが_定義された場合_ValueErrorのサブクラスである(self) -> None:
        assert issubclass(BinaryStringDecodeError, ValueError)

    def test_単体正常系_BinaryStringDecodeErrorが_値を受け取った場合_メッセージに値のrepr表現を含む(
        self,
    ) -> None:
        value = "not-a-valid-envelope"
        error = BinaryStringDecodeError(value)
        assert repr(value) in str(error)

    def test_単体正常系_BinaryStringDecodeErrorが_送出された場合_ValueErrorとして捕捉できる(self) -> None:
        with pytest.raises(ValueError):
            raise BinaryStringDecodeError(b"broken")


class TestObjectPickleError:
    def test_単体正常系_ObjectPickleErrorが_定義された場合_ValueErrorのサブクラスである(self) -> None:
        assert issubclass(ObjectPickleError, ValueError)

    def test_単体正常系_ObjectPickleErrorが_値を受け取った場合_メッセージに値のrepr表現を含む(self) -> None:
        value = object()
        error = ObjectPickleError(value)
        assert repr(value) in str(error)

    def test_単体正常系_ObjectPickleErrorが_送出された場合_ValueErrorとして捕捉できる(self) -> None:
        with pytest.raises(ValueError):
            raise ObjectPickleError(object())
