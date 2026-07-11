"""InvalidTimezoneError / DateTimeParseError の例外仕様を検証するテスト。"""

import pytest

from python_util.time_utility.exceptions import DateTimeParseError, InvalidTimezoneError


def test_単体正常系_InvalidTimezoneErrorが_定義された場合_ValueErrorのサブクラスである():
    assert issubclass(InvalidTimezoneError, ValueError)


def test_単体正常系_InvalidTimezoneErrorが_不正な値を渡された場合_メッセージにその値を含む():
    invalid_tz = "Asia/Tokio"

    with pytest.raises(InvalidTimezoneError) as exc_info:
        raise InvalidTimezoneError(invalid_tz)

    assert invalid_tz in str(exc_info.value)


def test_単体正常系_DateTimeParseErrorが_定義された場合_ValueErrorのサブクラスである():
    assert issubclass(DateTimeParseError, ValueError)


def test_単体正常系_DateTimeParseErrorが_不正な値を渡された場合_メッセージにその値を含む():
    invalid_text = "not-a-datetime"

    with pytest.raises(DateTimeParseError) as exc_info:
        raise DateTimeParseError(invalid_text)

    assert invalid_text in str(exc_info.value)
