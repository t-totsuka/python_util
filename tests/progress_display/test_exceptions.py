"""UnknownTaskError / InvalidTotalError / DisplayNotStartedError の例外仕様を検証するテスト。"""

import pytest

from python_util.progress_display.exceptions import (
    DisplayNotStartedError,
    InvalidTotalError,
    UnknownTaskError,
    _InvalidProgressDisplayConfig,
)


def test_単体正常系_UnknownTaskErrorが_定義された場合_ValueErrorのサブクラスである():
    assert issubclass(UnknownTaskError, ValueError)


def test_単体正常系_UnknownTaskErrorが_タスクIDを渡されて送出された場合_メッセージにタスクIDを含む():
    task_id = 42

    with pytest.raises(UnknownTaskError) as exc_info:
        raise UnknownTaskError(task_id)

    assert str(task_id) in str(exc_info.value)


def test_単体正常系_InvalidTotalErrorが_定義された場合_ValueErrorのサブクラスである():
    assert issubclass(InvalidTotalError, ValueError)


def test_単体正常系_InvalidTotalErrorが_不正なtotalを渡されて送出された場合_メッセージにtotalを含む():
    invalid_total = -1

    with pytest.raises(InvalidTotalError) as exc_info:
        raise InvalidTotalError(invalid_total)

    assert str(invalid_total) in str(exc_info.value)


def test_単体正常系_DisplayNotStartedErrorが_定義された場合_ValueErrorのサブクラスである():
    assert issubclass(DisplayNotStartedError, ValueError)


def test_単体正常系_DisplayNotStartedErrorが_引数なしで送出された場合_例外として送出できる():
    with pytest.raises(DisplayNotStartedError):
        raise DisplayNotStartedError()


def test_単体正常系_InvalidProgressDisplayConfigが_定義された場合_ValueErrorでないException派生である():
    assert issubclass(_InvalidProgressDisplayConfig, Exception)
    assert not issubclass(_InvalidProgressDisplayConfig, ValueError)
