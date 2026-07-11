"""python_util.time_utility パッケージの公開APIが集約されていることを確認するテスト。"""


def test_単体正常系_time_utilityパッケージの公開APIが_ルートからインポートされた場合_全てのシンボルを取得できる():
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


def test_結合_time_utilityパッケージの再エクスポートされたシンボルが_往復変換に使用された場合_元の値を保つ():
    from python_util.time_utility import DateTimeFormat, format_datetime, now, parse_datetime

    original = now()
    formatted = format_datetime(original, DateTimeFormat.ISO)
    parsed = parse_datetime(formatted)

    assert parsed == original
