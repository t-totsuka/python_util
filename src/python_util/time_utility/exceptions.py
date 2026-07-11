"""time_utility パッケージ固有の例外定義。"""

from __future__ import annotations


class InvalidTimezoneError(ValueError):
    """不正なタイムゾーン名またはタイムゾーンオブジェクトが指定された場合に送出される。"""

    def __init__(self, value: object) -> None:
        super().__init__(f"不正なタイムゾーンが指定されました: {value!r}")


class DateTimeParseError(ValueError):
    """日時文字列のパースに失敗した場合に送出される。"""

    def __init__(self, value: object) -> None:
        super().__init__(f"日時文字列のパースに失敗しました: {value!r}")
