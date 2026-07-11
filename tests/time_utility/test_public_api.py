"""python_util.time_utility パッケージの公開APIが集約されていることを確認するテスト。"""


def test_public_api_symbols_are_importable_from_package_root():
    from python_util.time_utility import (
        JST,
        DateTimeFormat,
        DateTimeParseError,
        InvalidTimezoneError,
        format_datetime,
        now,
        parse_datetime,
        to_jst,
        to_timezone,
        to_utc,
    )

    assert now is not None
    assert to_jst is not None
    assert to_utc is not None
    assert to_timezone is not None
    assert format_datetime is not None
    assert parse_datetime is not None
    assert JST is not None
    assert DateTimeFormat is not None
    assert InvalidTimezoneError is not None
    assert DateTimeParseError is not None


def test_public_api_round_trip_uses_reexported_symbols():
    from python_util.time_utility import DateTimeFormat, format_datetime, now, parse_datetime

    original = now()
    formatted = format_datetime(original, DateTimeFormat.ISO)
    parsed = parse_datetime(formatted)

    assert parsed == original
