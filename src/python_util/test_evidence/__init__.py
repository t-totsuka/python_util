"""pytest実行結果をMarkdownエビデンスとして記録するためのドメイン層。"""

from __future__ import annotations

from python_util.test_evidence.exceptions import InvalidReportDestinationError
from python_util.test_evidence.markdown_report import render_markdown_report
from python_util.test_evidence.report_writer import write_markdown_report
from python_util.test_evidence.types import TestCaseResult, TestOutcome, TestRunReport

__all__ = [
    "TestOutcome",
    "TestCaseResult",
    "TestRunReport",
    "render_markdown_report",
    "write_markdown_report",
    "InvalidReportDestinationError",
]
