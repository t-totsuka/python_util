"""InvalidTimezoneError / DateTimeParseError の例外仕様を検証するテスト。"""

import pytest

from python_util.time_utility.exceptions import DateTimeParseError, InvalidTimezoneError


def test_invalid_timezone_error_is_value_error():
    assert issubclass(InvalidTimezoneError, ValueError)


def test_invalid_timezone_error_message_contains_input_value():
    invalid_tz = "Asia/Tokio"

    with pytest.raises(InvalidTimezoneError) as exc_info:
        raise InvalidTimezoneError(invalid_tz)

    assert invalid_tz in str(exc_info.value)


def test_date_time_parse_error_is_value_error():
    assert issubclass(DateTimeParseError, ValueError)


def test_date_time_parse_error_message_contains_input_value():
    invalid_text = "not-a-datetime"

    with pytest.raises(DateTimeParseError) as exc_info:
        raise DateTimeParseError(invalid_text)

    assert invalid_text in str(exc_info.value)
