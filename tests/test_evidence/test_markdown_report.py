"""test_evidence.markdown_report のMarkdownレンダリングの仕様を検証するテスト。"""

from __future__ import annotations

from datetime import datetime

from python_util.test_evidence.markdown_report import render_markdown_report
from python_util.test_evidence.types import TestCaseResult, TestOutcome, TestRunReport


def _case(
    node_id: str,
    method_name: str,
    subpackage: str,
    outcome: TestOutcome,
    duration_seconds: float = 0.01,
    failure_message: str | None = None,
) -> TestCaseResult:
    return TestCaseResult(
        node_id=node_id,
        method_name=method_name,
        subpackage=subpackage,
        outcome=outcome,
        duration_seconds=duration_seconds,
        failure_message=failure_message,
    )


def test_単体正常系_render_markdown_reportが_複数サブパッケージのケースを受け取った場合_サブパッケージ単位で見出しをグルーピングして出力する():
    report = TestRunReport(
        cases=(
            _case("tests/logging/test_factory.py::test_x", "test_x", "logging", TestOutcome.PASSED),
            _case("tests/time_utility/test_clock.py::test_y", "test_y", "time_utility", TestOutcome.PASSED),
        ),
        started_at=datetime(2026, 7, 12, 10, 0, 0),
        finished_at=datetime(2026, 7, 12, 10, 0, 5),
    )

    markdown = render_markdown_report(report)

    logging_heading_index = markdown.index("### logging")
    time_utility_heading_index = markdown.index("### time_utility")
    assert markdown.index("test_x") > logging_heading_index
    assert markdown.index("test_y") > time_utility_heading_index


def test_単体正常系_render_markdown_reportが_成功失敗スキップを含む場合_全体サマリに件数と実行開始終了時刻を出力する():
    report = TestRunReport(
        cases=(
            _case("tests/logging/test_factory.py::test_a", "test_a", "logging", TestOutcome.PASSED),
            _case(
                "tests/logging/test_factory.py::test_b",
                "test_b",
                "logging",
                TestOutcome.FAILED,
                failure_message="AssertionError",
            ),
            _case("tests/logging/test_factory.py::test_c", "test_c", "logging", TestOutcome.SKIPPED),
        ),
        started_at=datetime(2026, 7, 12, 10, 0, 0),
        finished_at=datetime(2026, 7, 12, 10, 0, 5),
    )

    markdown = render_markdown_report(report)

    assert "合計: 3件" in markdown
    assert "成功: 1件" in markdown
    assert "失敗: 1件" in markdown
    assert "スキップ: 1件" in markdown
    assert "2026-07-12 10:00:00" in markdown
    assert "2026-07-12 10:00:05" in markdown


def test_単体正常系_render_markdown_reportが_失敗ケースを含む場合_専用セクションに失敗内容とともに明示する():
    report = TestRunReport(
        cases=(
            _case(
                "tests/logging/test_factory.py::test_y",
                "test_y",
                "logging",
                TestOutcome.FAILED,
                failure_message="AssertionError: 期待値と異なる",
            ),
        ),
        started_at=datetime(2026, 7, 12, 10, 0, 0),
        finished_at=datetime(2026, 7, 12, 10, 0, 1),
    )

    markdown = render_markdown_report(report)

    failure_section_index = markdown.index("## 失敗一覧")
    assert markdown.index("tests/logging/test_factory.py::test_y") > failure_section_index
    assert "AssertionError: 期待値と異なる" in markdown


def test_単体境界_render_markdown_reportが_0件のTestRunReportを受け取った場合_有効なMarkdownを返す():
    report = TestRunReport(
        cases=(),
        started_at=datetime(2026, 7, 12, 10, 0, 0),
        finished_at=datetime(2026, 7, 12, 10, 0, 0),
    )

    markdown = render_markdown_report(report)

    assert isinstance(markdown, str)
    assert markdown.strip() != ""
    assert "合計: 0件" in markdown
    assert "## 失敗一覧" not in markdown
