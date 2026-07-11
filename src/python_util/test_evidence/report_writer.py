"""Markdownレポートを描画し、指定パスへファイルとして書き込む。"""

from __future__ import annotations

from pathlib import Path

from python_util.test_evidence.exceptions import InvalidReportDestinationError
from python_util.test_evidence.markdown_report import render_markdown_report
from python_util.test_evidence.types import TestRunReport


def write_markdown_report(report: TestRunReport, destination: Path) -> None:
    """TestRunReportをMarkdownとして描画し、destinationへ書き込む。"""
    if destination.suffix != ".md":
        raise InvalidReportDestinationError(destination)

    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_markdown_report(report), encoding="utf-8")
