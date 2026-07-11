"""formatting.DateTimeFormat / format_datetime の仕様を検証するテスト。"""

from __future__ import annotations

from datetime import datetime

import pytest

from python_util.time_utility.exceptions import DateTimeParseError
from python_util.time_utility.formatting import DateTimeFormat, format_datetime, parse_datetime
from python_util.time_utility.timezones import JST
from python_util.time_utility.convert import UTC


def test_単体正常系_DateTimeFormatが_列挙型として定義された場合_全ての事前定義メンバーを持つ():
    assert DateTimeFormat.ISO.value == "iso"
    assert DateTimeFormat.DATE.value == "date"
    assert DateTimeFormat.DATETIME.value == "datetime"
    assert DateTimeFormat.JAPANESE_DATE.value == "japanese_date"
    assert DateTimeFormat.JAPANESE_DATETIME.value == "japanese_datetime"


def test_単体正常系_format_datetimeが_ISO形式でaware状態のdatetimeを受け取った場合_UTCオフセットを含む文字列を返す():
    aware = datetime(2026, 7, 11, 9, 0, 0, tzinfo=JST)

    result = format_datetime(aware, DateTimeFormat.ISO)

    assert result == "2026-07-11T09:00:00+09:00"


def test_単体正常系_format_datetimeが_DATE形式を指定された場合_年月日形式の文字列を返す():
    dt = datetime(2026, 7, 11, 9, 0, 0)

    result = format_datetime(dt, DateTimeFormat.DATE)

    assert result == "2026-07-11"


def test_単体正常系_format_datetimeが_DATETIME形式を指定された場合_年月日時分秒形式の文字列を返す():
    dt = datetime(2026, 7, 11, 9, 5, 30)

    result = format_datetime(dt, DateTimeFormat.DATETIME)

    assert result == "2026-07-11 09:05:30"


def test_単体正常系_format_datetimeが_fmtを省略された場合_DATETIME形式の文字列を返す():
    dt = datetime(2026, 7, 11, 9, 5, 30)

    result = format_datetime(dt)

    assert result == "2026-07-11 09:05:30"


def test_単体正常系_format_datetimeが_JAPANESE_DATE形式を指定された場合_ロケール非依存で曜日を含む文字列を返す():
    dt = datetime(2026, 7, 11, 9, 0, 0)

    result = format_datetime(dt, DateTimeFormat.JAPANESE_DATE)

    assert result == "2026年07月11日(土)"


def test_単体正常系_format_datetimeが_JAPANESE_DATETIME形式を指定された場合_曜日と時刻を含む文字列を返す():
    dt = datetime(2026, 7, 11, 9, 5, 30)

    result = format_datetime(dt, DateTimeFormat.JAPANESE_DATETIME)

    assert result == "2026年07月11日(土) 09:05:30"


def test_単体正常系_format_datetimeが_enum値と一致する文字列でfmtを指定された場合_対応する形式の文字列を返す():
    dt = datetime(2026, 7, 11, 9, 5, 30)

    result = format_datetime(dt, "japanese_date")

    assert result == "2026年07月11日(土)"


def test_単体正常系_format_datetimeが_enumにないstrftime書式文字列を指定された場合_その書式で文字列を返す():
    dt = datetime(2026, 7, 11, 9, 5, 30)

    result = format_datetime(dt, "%Y/%m/%d")

    assert result == "2026/07/11"


def test_異常系_format_datetimeが_datetime以外を受け取った場合_TypeErrorを送出する():
    with pytest.raises(TypeError):
        format_datetime(None, DateTimeFormat.DATE)


def test_単体正常系_parse_datetimeが_ISO形式の文字列を受け取った場合_aware状態のdatetimeへ往復変換する():
    aware = datetime(2026, 7, 11, 9, 0, 0, tzinfo=JST)
    text = format_datetime(aware, DateTimeFormat.ISO)

    result = parse_datetime(text)

    assert result == aware
    assert result.tzinfo is not None


def test_単体正常系_parse_datetimeが_DATETIME形式の文字列を受け取った場合_aware状態のdatetimeへ往復変換する():
    aware = datetime(2026, 7, 11, 9, 5, 30, tzinfo=JST)
    text = format_datetime(aware, DateTimeFormat.DATETIME)

    result = parse_datetime(text)

    assert result == aware


def test_単体正常系_parse_datetimeが_DATE形式の文字列を受け取った場合_aware状態のdatetimeへ往復変換する():
    aware = datetime(2026, 7, 11, 0, 0, 0, tzinfo=JST)
    text = format_datetime(aware, DateTimeFormat.DATE)

    result = parse_datetime(text)

    assert result == aware


def test_単体正常系_parse_datetimeが_JAPANESE_DATETIME形式の文字列を受け取った場合_aware状態のdatetimeへ往復変換する():
    aware = datetime(2026, 7, 11, 9, 5, 30, tzinfo=JST)
    text = format_datetime(aware, DateTimeFormat.JAPANESE_DATETIME)

    result = parse_datetime(text)

    assert result == aware


def test_単体正常系_parse_datetimeが_JAPANESE_DATE形式の文字列を受け取った場合_aware状態のdatetimeへ往復変換する():
    aware = datetime(2026, 7, 11, 0, 0, 0, tzinfo=JST)
    text = format_datetime(aware, DateTimeFormat.JAPANESE_DATE)

    result = parse_datetime(text)

    assert result == aware


def test_単体正常系_parse_datetimeが_タイムゾーン情報のない文字列を受け取った場合_デフォルトでJSTを付与する():
    result = parse_datetime("2026-07-11 09:05:30")

    assert result == datetime(2026, 7, 11, 9, 5, 30, tzinfo=JST)


def test_単体正常系_parse_datetimeが_タイムゾーン情報のない文字列とtzを指定された場合_指定したタイムゾーンを付与する():
    result = parse_datetime("2026-07-11 09:05:30", tz=UTC)

    assert result == datetime(2026, 7, 11, 9, 5, 30, tzinfo=UTC)


def test_単体正常系_parse_datetimeが_fmtにenumを明示指定された場合_その形式のみで解析する():
    result = parse_datetime("2026-07-11", DateTimeFormat.DATE)

    assert result == datetime(2026, 7, 11, tzinfo=JST)


def test_単体正常系_parse_datetimeが_fmtに文字列値を明示指定された場合_その形式のみで解析する():
    result = parse_datetime("2026年07月11日(土)", "japanese_date")

    assert result == datetime(2026, 7, 11, tzinfo=JST)


def test_単体正常系_parse_datetimeが_enumにないstrptime書式文字列を指定された場合_その書式で解析する():
    result = parse_datetime("2026/07/11", fmt="%Y/%m/%d")

    assert result == datetime(2026, 7, 11, tzinfo=JST)


def test_異常系_parse_datetimeが_いずれの形式にも一致しない文字列を受け取った場合_DateTimeParseErrorを送出する():
    with pytest.raises(DateTimeParseError):
        parse_datetime("not a datetime")


def test_異常系_parse_datetimeが_指定した形式に一致しない文字列を受け取った場合_DateTimeParseErrorを送出する():
    with pytest.raises(DateTimeParseError):
        parse_datetime("2026年07月11日(土)", DateTimeFormat.DATE)
