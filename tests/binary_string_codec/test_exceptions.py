"""exceptions モジュールのテスト。"""

from __future__ import annotations

import pytest

from python_util.binary_string_codec.exceptions import (
    BinaryStringDecodeError,
    ObjectPickleError,
)


class TestBinaryStringDecodeError:
    def test_is_value_error_subclass(self) -> None:
        assert issubclass(BinaryStringDecodeError, ValueError)

    def test_message_contains_value(self) -> None:
        value = "not-a-valid-envelope"
        error = BinaryStringDecodeError(value)
        assert repr(value) in str(error)

    def test_raise_and_catch_as_value_error(self) -> None:
        with pytest.raises(ValueError):
            raise BinaryStringDecodeError(b"broken")


class TestObjectPickleError:
    def test_is_value_error_subclass(self) -> None:
        assert issubclass(ObjectPickleError, ValueError)

    def test_message_contains_value(self) -> None:
        value = object()
        error = ObjectPickleError(value)
        assert repr(value) in str(error)

    def test_raise_and_catch_as_value_error(self) -> None:
        with pytest.raises(ValueError):
            raise ObjectPickleError(object())
