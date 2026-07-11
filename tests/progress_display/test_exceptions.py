"""UnknownTaskError / InvalidTotalError / DisplayNotStartedError の例外仕様を検証するテスト。"""

import pytest

from python_util.progress_display.exceptions import (
    DisplayNotStartedError,
    InvalidTotalError,
    UnknownTaskError,
    _InvalidProgressDisplayConfig,
)


def test_unknown_task_error_is_value_error():
    assert issubclass(UnknownTaskError, ValueError)


def test_unknown_task_error_message_contains_task_id():
    task_id = 42

    with pytest.raises(UnknownTaskError) as exc_info:
        raise UnknownTaskError(task_id)

    assert str(task_id) in str(exc_info.value)


def test_invalid_total_error_is_value_error():
    assert issubclass(InvalidTotalError, ValueError)


def test_invalid_total_error_message_contains_total():
    invalid_total = -1

    with pytest.raises(InvalidTotalError) as exc_info:
        raise InvalidTotalError(invalid_total)

    assert str(invalid_total) in str(exc_info.value)


def test_display_not_started_error_is_value_error():
    assert issubclass(DisplayNotStartedError, ValueError)


def test_display_not_started_error_can_be_raised_without_arguments():
    with pytest.raises(DisplayNotStartedError):
        raise DisplayNotStartedError()


def test_invalid_progress_display_config_is_not_value_error():
    assert issubclass(_InvalidProgressDisplayConfig, Exception)
    assert not issubclass(_InvalidProgressDisplayConfig, ValueError)
