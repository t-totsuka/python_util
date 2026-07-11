"""test_evidence.types の値オブジェクトの仕様を検証するテスト。"""

import dataclasses
from datetime import datetime

import pytest

from python_util.test_evidence.types import TestCaseResult, TestOutcome, TestRunReport


def test_単体正常系_TestOutcomeが_4値を持つ場合_それぞれの値でアクセスできる():
    assert TestOutcome.PASSED.value == "passed"
    assert TestOutcome.FAILED.value == "failed"
    assert TestOutcome.SKIPPED.value == "skipped"
    assert TestOutcome.ERROR.value == "error"


def test_単体正常系_TestCaseResultが_必須項目を受け取った場合_各属性を保持する():
    result = TestCaseResult(
        node_id="tests/logging/test_factory.py::test_x",
        method_name="test_x",
        subpackage="logging",
        outcome=TestOutcome.PASSED,
        duration_seconds=0.01,
    )

    assert result.node_id == "tests/logging/test_factory.py::test_x"
    assert result.method_name == "test_x"
    assert result.subpackage == "logging"
    assert result.outcome is TestOutcome.PASSED
    assert result.duration_seconds == 0.01
    assert result.failure_message is None


def test_単体正常系_TestCaseResultが_failure_messageを受け取った場合_属性に保持する():
    result = TestCaseResult(
        node_id="tests/logging/test_factory.py::test_y",
        method_name="test_y",
        subpackage="logging",
        outcome=TestOutcome.FAILED,
        duration_seconds=0.02,
        failure_message="AssertionError: 期待値と異なる",
    )

    assert result.failure_message == "AssertionError: 期待値と異なる"


def test_単体正常系_TestCaseResultが_生成済みの場合_属性への再代入でFrozenInstanceErrorを送出する():
    result = TestCaseResult(
        node_id="tests/logging/test_factory.py::test_x",
        method_name="test_x",
        subpackage="logging",
        outcome=TestOutcome.PASSED,
        duration_seconds=0.01,
    )

    with pytest.raises(dataclasses.FrozenInstanceError):
        result.outcome = TestOutcome.FAILED


def test_単体正常系_TestRunReportが_複数のTestCaseResultを受け取った場合_全件を保持する():
    started_at = datetime(2026, 7, 12, 10, 0, 0)
    finished_at = datetime(2026, 7, 12, 10, 0, 5)
    case = TestCaseResult(
        node_id="tests/logging/test_factory.py::test_x",
        method_name="test_x",
        subpackage="logging",
        outcome=TestOutcome.PASSED,
        duration_seconds=0.01,
    )

    report = TestRunReport(cases=(case,), started_at=started_at, finished_at=finished_at)

    assert report.cases == (case,)
    assert report.started_at == started_at
    assert report.finished_at == finished_at


def test_単体正常系_TestRunReportが_生成済みの場合_属性への再代入でFrozenInstanceErrorを送出する():
    report = TestRunReport(cases=(), started_at=datetime(2026, 7, 12), finished_at=datetime(2026, 7, 12))

    with pytest.raises(dataclasses.FrozenInstanceError):
        report.cases = ()
