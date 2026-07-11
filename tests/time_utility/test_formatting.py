"""formatting.DateTimeFormat / format_datetime の仕様を検証するテスト。"""

from __future__ import annotations

from datetime import datetime

import pytest

from python_util.time_utility.exceptions import DateTimeParseError
from python_util.time_utility.formatting import DateTimeFormat, format_datetime, parse_datetime
from python_util.time_utility.timezones import JST
from python_util.time_utility.convert import UTC


def test_date_time_format_enum_has_all_predefined_members():
    assert DateTimeFormat.ISO.value == "iso"
    assert DateTimeFormat.DATE.value == "date"
    assert DateTimeFormat.DATETIME.value == "datetime"
    assert DateTimeFormat.JAPANESE_DATE.value == "japanese_date"
    assert DateTimeFormat.JAPANESE_DATETIME.value == "japanese_datetime"


def test_format_datetime_iso_includes_utc_offset_for_aware_datetime():
    aware = datetime(2026, 7, 11, 9, 0, 0, tzinfo=JST)

    result = format_datetime(aware, DateTimeFormat.ISO)

    assert result == "2026-07-11T09:00:00+09:00"


def test_format_datetime_date_returns_year_month_day():
    dt = datetime(2026, 7, 11, 9, 0, 0)

    result = format_datetime(dt, DateTimeFormat.DATE)

    assert result == "2026-07-11"


def test_format_datetime_datetime_returns_year_month_day_hour_minute_second():
    dt = datetime(2026, 7, 11, 9, 5, 30)

    result = format_datetime(dt, DateTimeFormat.DATETIME)

    assert result == "2026-07-11 09:05:30"


def test_format_datetime_defaults_to_datetime_format_when_fmt_omitted():
    dt = datetime(2026, 7, 11, 9, 5, 30)

    result = format_datetime(dt)

    assert result == "2026-07-11 09:05:30"


def test_format_datetime_japanese_date_includes_weekday_without_locale():
    dt = datetime(2026, 7, 11, 9, 0, 0)

    result = format_datetime(dt, DateTimeFormat.JAPANESE_DATE)

    assert result == "2026年07月11日(土)"


def test_format_datetime_japanese_datetime_includes_weekday_and_time():
    dt = datetime(2026, 7, 11, 9, 5, 30)

    result = format_datetime(dt, DateTimeFormat.JAPANESE_DATETIME)

    assert result == "2026年07月11日(土) 09:05:30"


def test_format_datetime_accepts_format_string_matching_enum_value():
    dt = datetime(2026, 7, 11, 9, 5, 30)

    result = format_datetime(dt, "japanese_date")

    assert result == "2026年07月11日(土)"


def test_format_datetime_accepts_custom_strftime_string_not_in_enum():
    dt = datetime(2026, 7, 11, 9, 5, 30)

    result = format_datetime(dt, "%Y/%m/%d")

    assert result == "2026/07/11"


def test_format_datetime_raises_type_error_for_non_datetime():
    with pytest.raises(TypeError):
        format_datetime(None, DateTimeFormat.DATE)


def test_parse_datetime_iso_round_trips_aware_datetime():
    aware = datetime(2026, 7, 11, 9, 0, 0, tzinfo=JST)
    text = format_datetime(aware, DateTimeFormat.ISO)

    result = parse_datetime(text)

    assert result == aware
    assert result.tzinfo is not None


def test_parse_datetime_datetime_format_round_trips_aware_datetime():
    aware = datetime(2026, 7, 11, 9, 5, 30, tzinfo=JST)
    text = format_datetime(aware, DateTimeFormat.DATETIME)

    result = parse_datetime(text)

    assert result == aware


def test_parse_datetime_date_format_round_trips_aware_datetime():
    aware = datetime(2026, 7, 11, 0, 0, 0, tzinfo=JST)
    text = format_datetime(aware, DateTimeFormat.DATE)

    result = parse_datetime(text)

    assert result == aware


def test_parse_datetime_japanese_datetime_format_round_trips_aware_datetime():
    aware = datetime(2026, 7, 11, 9, 5, 30, tzinfo=JST)
    text = format_datetime(aware, DateTimeFormat.JAPANESE_DATETIME)

    result = parse_datetime(text)

    assert result == aware


def test_parse_datetime_japanese_date_format_round_trips_aware_datetime():
    aware = datetime(2026, 7, 11, 0, 0, 0, tzinfo=JST)
    text = format_datetime(aware, DateTimeFormat.JAPANESE_DATE)

    result = parse_datetime(text)

    assert result == aware


def test_parse_datetime_without_timezone_info_defaults_to_jst():
    result = parse_datetime("2026-07-11 09:05:30")

    assert result == datetime(2026, 7, 11, 9, 5, 30, tzinfo=JST)


def test_parse_datetime_without_timezone_info_uses_explicit_tz_when_given():
    result = parse_datetime("2026-07-11 09:05:30", tz=UTC)

    assert result == datetime(2026, 7, 11, 9, 5, 30, tzinfo=UTC)


def test_parse_datetime_with_explicit_fmt_enum_matches_only_that_format():
    result = parse_datetime("2026-07-11", DateTimeFormat.DATE)

    assert result == datetime(2026, 7, 11, tzinfo=JST)


def test_parse_datetime_with_explicit_fmt_string_value_matches_only_that_format():
    result = parse_datetime("2026年07月11日(土)", "japanese_date")

    assert result == datetime(2026, 7, 11, tzinfo=JST)


def test_parse_datetime_accepts_custom_strptime_string_not_in_enum():
    result = parse_datetime("2026/07/11", fmt="%Y/%m/%d")

    assert result == datetime(2026, 7, 11, tzinfo=JST)


def test_parse_datetime_raises_error_when_text_does_not_match_any_format():
    with pytest.raises(DateTimeParseError):
        parse_datetime("not a datetime")


def test_parse_datetime_raises_error_when_text_does_not_match_specified_format():
    with pytest.raises(DateTimeParseError):
        parse_datetime("2026年07月11日(土)", DateTimeFormat.DATE)
