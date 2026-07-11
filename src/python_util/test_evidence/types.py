"""テスト実行結果を表現する値オブジェクトの定義。"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class TestOutcome(str, Enum):
    """pytestの結果分類を表す列挙型。"""

    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass(frozen=True)
class TestCaseResult:
    """1テストケースの実行結果を保持するイミュータブルな値オブジェクト。"""

    node_id: str
    method_name: str
    subpackage: str
    outcome: TestOutcome
    duration_seconds: float
    failure_message: str | None = None


@dataclass(frozen=True)
class TestRunReport:
    """1回のpytestセッションの実行結果を集約するイミュータブルな値オブジェクト。"""

    cases: tuple[TestCaseResult, ...]
    started_at: datetime
    finished_at: datetime
