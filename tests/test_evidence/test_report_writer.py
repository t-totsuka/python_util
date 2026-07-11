"""test_evidence.report_writer のファイル書き込み仕様を検証するテスト。"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pytest

from python_util.test_evidence.exceptions import InvalidReportDestinationError
from python_util.test_evidence.markdown_report import render_markdown_report
from python_util.test_evidence.report_writer import write_markdown_report
from python_util.test_evidence.types import TestCaseResult, TestOutcome, TestRunReport


def _report() -> TestRunReport:
    case = TestCaseResult(
        node_id="tests/logging/test_factory.py::test_x",
        method_name="test_x",
        subpackage="logging",
        outcome=TestOutcome.PASSED,
        duration_seconds=0.01,
    )
    return TestRunReport(
        cases=(case,),
        started_at=datetime(2026, 7, 12, 10, 0, 0),
        finished_at=datetime(2026, 7, 12, 10, 0, 5),
    )


def test_単体正常系_write_markdown_reportが_有効な出力先を受け取った場合_render結果をファイルへ書き込む(tmp_path: Path):
    destination = tmp_path / "reports" / "test-evidence.md"

    write_markdown_report(_report(), destination)

    assert destination.read_text(encoding="utf-8") == render_markdown_report(_report())


def test_単体正常系_write_markdown_reportが_親ディレクトリが存在しない場合_ディレクトリを作成してから書き込む(tmp_path: Path):
    destination = tmp_path / "nested" / "dir" / "test-evidence.md"

    write_markdown_report(_report(), destination)

    assert destination.exists()
    assert destination.parent.is_dir()


def test_単体正常系_write_markdown_reportが_再実行された場合_内容を上書きする(tmp_path: Path):
    destination = tmp_path / "test-evidence.md"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text("古い内容", encoding="utf-8")

    write_markdown_report(_report(), destination)

    assert "古い内容" not in destination.read_text(encoding="utf-8")


def test_単体異常系_write_markdown_reportが_md以外の拡張子を受け取った場合_InvalidReportDestinationErrorを送出する(tmp_path: Path):
    destination = tmp_path / "test-evidence.txt"

    with pytest.raises(InvalidReportDestinationError):
        write_markdown_report(_report(), destination)

    assert not destination.exists()
