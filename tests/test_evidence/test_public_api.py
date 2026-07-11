"""test_evidence パッケージの公開API限定エクスポートを検証するテスト。"""

from __future__ import annotations

import python_util.test_evidence as test_evidence


def test_単体正常系_test_evidenceパッケージが_importされた場合_公開APIをall属性として保持する():
    assert set(test_evidence.__all__) == {
        "TestOutcome",
        "TestCaseResult",
        "TestRunReport",
        "render_markdown_report",
        "write_markdown_report",
        "InvalidReportDestinationError",
    }


def test_単体正常系_test_evidenceパッケージが_importされた場合_all属性に列挙した名前を実際に参照できる():
    for name in test_evidence.__all__:
        assert hasattr(test_evidence, name)
