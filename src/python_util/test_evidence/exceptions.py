"""test_evidence パッケージ固有の例外定義。"""

from __future__ import annotations


class InvalidReportDestinationError(ValueError):
    """write_markdown_report の destination が .md 拡張子でない場合に送出される。"""

    def __init__(self, destination: object) -> None:
        super().__init__(f"出力先の拡張子が.mdではありません: {destination!r}")
