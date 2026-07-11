"""test_evidence.exceptions の専用例外の仕様を検証するテスト。"""

from __future__ import annotations

import pytest

from python_util.test_evidence.exceptions import InvalidReportDestinationError


def test_単体正常系_InvalidReportDestinationErrorが_ValueErrorを継承している場合_ValueErrorとして送出できる():
    with pytest.raises(ValueError):
        raise InvalidReportDestinationError("reports/test-evidence.txt")


def test_単体異常系_InvalidReportDestinationErrorが_不正な拡張子を受け取った場合_送出先を含むメッセージを保持する():
    with pytest.raises(InvalidReportDestinationError) as exc_info:
        raise InvalidReportDestinationError("reports/test-evidence.txt")

    assert "reports/test-evidence.txt" in str(exc_info.value)
