"""pytest実行結果を収集しテストエビデンスへ変換するリポジトリルートのフック定義。"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import pytest

from python_util.test_evidence.report_writer import write_markdown_report
from python_util.test_evidence.types import TestCaseResult, TestOutcome, TestRunReport

pytest_plugins = ["pytester"]

EVIDENCE_DESTINATION = Path("reports/test-evidence.md")


@dataclass
class _CollectorState:
    """1つのpytestセッションに対応する収集状態。pytesterによるネストしたセッションと分離するためスタックで管理する。"""

    collected_results: list[TestCaseResult] = field(default_factory=list)
    pending_reports: dict[str, dict[str, pytest.TestReport]] = field(default_factory=dict)
    session_started_at: datetime | None = None


_state_stack: list[_CollectorState] = []


def _current_state() -> _CollectorState:
    return _state_stack[-1]


def __getattr__(name: str) -> Any:
    if name == "collected_results":
        return _current_state().collected_results
    raise AttributeError(name)


def pytest_configure(config: pytest.Config) -> None:
    """セッション開始時に専用の収集状態をスタックへ積む。ネストしたpytesterセッションが自身の状態のみを操作するようにする。"""
    _state_stack.append(_CollectorState())


def pytest_unconfigure(config: pytest.Config) -> None:
    """セッション終了時に収集状態をスタックから取り除き、外側セッションの状態へ復帰する。"""
    _state_stack.pop()


def _extract_subpackage_and_method_name(node_id: str) -> tuple[str, str]:
    """nodeidからサブパッケージ名（tests/直下のディレクトリ名）とメソッド名を抽出する。"""
    segments = node_id.split("::")
    file_path_parts = Path(segments[0]).parts
    subpackage = file_path_parts[1] if len(file_path_parts) > 1 else ""
    method_name = segments[-1]
    return subpackage, method_name


def _determine_outcome(phase_reports: dict[str, pytest.TestReport]) -> TestOutcome:
    """setup/call/teardownの3フェーズの結果からテストケース全体の結果を確定する。"""
    if any(report.outcome == "failed" for report in phase_reports.values()):
        return TestOutcome.FAILED
    setup_report = phase_reports.get("setup")
    if setup_report is not None and setup_report.outcome == "skipped":
        return TestOutcome.SKIPPED
    return TestOutcome.PASSED


def _build_failure_message(phase_reports: dict[str, pytest.TestReport]) -> str | None:
    """失敗・エラーとなったフェーズの内容からfailure_messageを組み立てる。"""
    failed_reports = [report for report in phase_reports.values() if report.outcome == "failed"]
    if not failed_reports:
        return None
    return "\n".join(f"[{report.when}] {report.longreprtext}" for report in failed_reports)


def pytest_runtest_logreport(report: pytest.TestReport) -> None:
    """setup/call/teardown各フェーズの結果をnodeid単位で集約し、teardown完了時にTestCaseResultを確定する。"""
    state = _current_state()
    phase_reports = state.pending_reports.setdefault(report.nodeid, {})
    phase_reports[report.when] = report

    if report.when != "teardown":
        return

    outcome = _determine_outcome(phase_reports)
    subpackage, method_name = _extract_subpackage_and_method_name(report.nodeid)
    duration_seconds = sum(r.duration for r in phase_reports.values())
    failure_message = _build_failure_message(phase_reports)

    state.collected_results.append(
        TestCaseResult(
            node_id=report.nodeid,
            method_name=method_name,
            subpackage=subpackage,
            outcome=outcome,
            duration_seconds=duration_seconds,
            failure_message=failure_message,
        )
    )
    del state.pending_reports[report.nodeid]


def pytest_sessionstart(session: pytest.Session) -> None:
    """pytestセッションの開始時刻を記録する。"""
    _current_state().session_started_at = datetime.now()


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    """セッション終了時刻を記録し、収集済みのTestCaseResult群からTestRunReportを組み立ててMarkdownエビデンスへ書き込む。"""
    finished_at = datetime.now()
    state = _current_state()
    started_at = state.session_started_at if state.session_started_at is not None else finished_at
    report = TestRunReport(cases=tuple(state.collected_results), started_at=started_at, finished_at=finished_at)
    write_markdown_report(report, EVIDENCE_DESTINATION)
