"""clock.now の仕様を検証するテスト。"""

from __future__ import annotations

from zoneinfo import ZoneInfo

import pytest

from python_util.time_utility.clock import now
from python_util.time_utility.exceptions import InvalidTimezoneError
from python_util.time_utility.timezones import JST


def test_単体正常系_nowが_tzを指定せずに呼ばれた場合_JSTタイムゾーンのdatetimeを返す():
    result = now()

    assert result.tzinfo is JST


def test_単体正常系_nowが_文字列でタイムゾーンを指定された場合_指定したタイムゾーンのdatetimeを返す():
    result = now(tz="UTC")

    assert result.tzinfo == ZoneInfo("UTC")


def test_単体正常系_nowが_tzinfoオブジェクトを指定された場合_同じtzinfoを返す():
    tz = ZoneInfo("America/New_York")

    result = now(tz=tz)

    assert result.tzinfo is tz


def test_異常系_nowが_サポート対象外の型を指定された場合_TypeErrorを送出する():
    with pytest.raises(TypeError):
        now(tz=123)


def test_異常系_nowが_未知のタイムゾーン名を指定された場合_InvalidTimezoneErrorを送出する():
    with pytest.raises(InvalidTimezoneError):
        now(tz="Asia/Tokio")
