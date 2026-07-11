"""convert.ensure_aware / to_jst / to_utc / to_timezone の仕様を検証するテスト。"""

from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest

from python_util.time_utility.convert import ensure_aware, to_jst, to_timezone, to_utc
from python_util.time_utility.exceptions import InvalidTimezoneError
from python_util.time_utility.timezones import JST

UTC = ZoneInfo("UTC")


def test_単体正常系_ensure_awareが_naive状態のdatetimeを受け取った場合_デフォルトでJSTを付与する():
    naive = datetime(2026, 7, 11, 9, 0, 0)

    result = ensure_aware(naive)

    assert result.tzinfo is JST
    assert (result.year, result.month, result.day, result.hour) == (2026, 7, 11, 9)


def test_単体正常系_ensure_awareが_aware状態のdatetimeを受け取った場合_変更せずそのまま返す():
    aware = datetime(2026, 7, 11, 9, 0, 0, tzinfo=UTC)

    result = ensure_aware(aware)

    assert result == aware
    assert result.tzinfo is UTC


def test_単体正常系_ensure_awareが_naive状態のdatetimeとdefault_tzを指定された場合_指定したタイムゾーンを付与する():
    naive = datetime(2026, 7, 11, 9, 0, 0)

    result = ensure_aware(naive, default_tz=UTC)

    assert result.tzinfo is UTC


def test_単体正常系_ensure_awareが_aware状態のdatetimeとdefault_tzを指定された場合_default_tzを無視する():
    aware = datetime(2026, 7, 11, 9, 0, 0, tzinfo=UTC)

    result = ensure_aware(aware, default_tz=JST)

    assert result.tzinfo is UTC


def test_異常系_ensure_awareが_datetime以外を受け取った場合_TypeErrorを送出する():
    with pytest.raises(TypeError):
        ensure_aware(None)


def test_単体正常系_to_jstが_aware状態のdatetimeを受け取った場合_同一時刻を保ったままJSTへ変換する():
    aware_utc = datetime(2026, 7, 11, 0, 0, 0, tzinfo=UTC)

    result = to_jst(aware_utc)

    assert result.tzinfo is JST
    assert result == aware_utc
    assert result.hour == 9


def test_単体正常系_to_jstが_naive状態のdatetimeを受け取った場合_既にJSTとして扱う():
    naive = datetime(2026, 7, 11, 9, 0, 0)

    result = to_jst(naive)

    assert result.tzinfo is JST
    assert (result.year, result.month, result.day, result.hour) == (2026, 7, 11, 9)


def test_異常系_to_jstが_datetime以外を受け取った場合_TypeErrorを送出する():
    with pytest.raises(TypeError):
        to_jst(None)


def test_単体正常系_to_utcが_naive状態のdatetimeを受け取った場合_JSTとして解釈しUTCへ変換する():
    naive = datetime(2026, 7, 11, 9, 0, 0)

    result = to_utc(naive)

    assert result.tzinfo is not None
    assert result.utcoffset() == timedelta(0)
    assert result.hour == 0
    assert result.day == 11


def test_単体正常系_to_utcが_aware状態のdatetimeを受け取った場合_同一時刻を保ったままUTCへ変換する():
    aware_jst = datetime(2026, 7, 11, 9, 0, 0, tzinfo=JST)

    result = to_utc(aware_jst)

    assert result.utcoffset() == timedelta(0)
    assert result == aware_jst
    assert result.hour == 0


def test_異常系_to_utcが_datetime以外を受け取った場合_TypeErrorを送出する():
    with pytest.raises(TypeError):
        to_utc(None)


def test_単体正常系_to_timezoneが_文字列でタイムゾーンを指定された場合_指定したタイムゾーンへ変換する():
    aware_jst = datetime(2026, 7, 11, 9, 0, 0, tzinfo=JST)

    result = to_timezone(aware_jst, "America/New_York")

    assert result.tzinfo == ZoneInfo("America/New_York")
    assert result == aware_jst


def test_単体正常系_to_timezoneが_naive状態のdatetimeを受け取った場合_JSTとして解釈してから変換する():
    naive = datetime(2026, 7, 11, 9, 0, 0)

    result = to_timezone(naive, UTC)

    assert result.tzinfo is UTC
    assert result.hour == 0


def test_異常系_to_timezoneが_未知のタイムゾーン名を指定された場合_InvalidTimezoneErrorを送出する():
    aware_jst = datetime(2026, 7, 11, 9, 0, 0, tzinfo=JST)

    with pytest.raises(InvalidTimezoneError):
        to_timezone(aware_jst, "Asia/Tokio")


def test_異常系_to_timezoneが_datetime以外を受け取った場合_TypeErrorを送出する():
    with pytest.raises(TypeError):
        to_timezone(None, UTC)


def test_結合_to_utcとto_jstが_aware状態のdatetimeを往復変換した場合_元の値を保つ():
    original = datetime(2026, 7, 11, 9, 0, 0, tzinfo=JST)

    round_tripped = to_jst(to_utc(original))

    assert round_tripped == original
    assert round_tripped.tzinfo is JST


def test_結合_to_utcとto_jstが_naive状態のdatetimeを往復変換した場合_元の時刻表記を保つ():
    naive = datetime(2026, 7, 11, 9, 0, 0)

    round_tripped = to_jst(to_utc(naive))

    assert (round_tripped.year, round_tripped.month, round_tripped.day, round_tripped.hour) == (
        2026,
        7,
        11,
        9,
    )
