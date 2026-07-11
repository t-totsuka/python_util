"""TestRunReportからMarkdown形式のテスト結果レポート文字列を描画する。"""

from __future__ import annotations

from python_util.test_evidence.types import TestCaseResult, TestOutcome, TestRunReport

_OUTCOME_LABELS: dict[TestOutcome, str] = {
    TestOutcome.PASSED: "成功",
    TestOutcome.FAILED: "失敗",
    TestOutcome.SKIPPED: "スキップ",
    TestOutcome.ERROR: "エラー",
}

_FAILURE_OUTCOMES = (TestOutcome.FAILED, TestOutcome.ERROR)


def render_markdown_report(report: TestRunReport) -> str:
    """TestRunReportからMarkdown形式のテスト結果レポート文字列を描画する。"""
    lines: list[str] = ["# テスト実行結果エビデンス", "", "## サマリ", ""]
    lines.extend(_render_summary(report))
    lines.append("")

    failures = tuple(case for case in report.cases if case.outcome in _FAILURE_OUTCOMES)
    if failures:
        lines.append("## 失敗一覧")
        lines.append("")
        for case in failures:
            lines.extend(_render_failure(case))

    lines.append("## テスト結果")
    lines.append("")
    lines.extend(_render_subpackages(report.cases))

    return "\n".join(lines).rstrip() + "\n"


def _render_summary(report: TestRunReport) -> list[str]:
    cases = report.cases
    counts = {outcome: 0 for outcome in TestOutcome}
    for case in cases:
        counts[case.outcome] += 1

    return [
        f"- 実行開始: {report.started_at:%Y-%m-%d %H:%M:%S}",
        f"- 実行終了: {report.finished_at:%Y-%m-%d %H:%M:%S}",
        f"- 合計: {len(cases)}件",
        f"- 成功: {counts[TestOutcome.PASSED]}件",
        f"- 失敗: {counts[TestOutcome.FAILED]}件",
        f"- エラー: {counts[TestOutcome.ERROR]}件",
        f"- スキップ: {counts[TestOutcome.SKIPPED]}件",
    ]


def _render_failure(case: TestCaseResult) -> list[str]:
    return [
        f"### {case.node_id}",
        "",
        f"- 結果: {_OUTCOME_LABELS[case.outcome]}",
        "- 失敗内容:",
        "",
        "```",
        case.failure_message or "(詳細なし)",
        "```",
        "",
    ]


def _render_subpackages(cases: tuple[TestCaseResult, ...]) -> list[str]:
    if not cases:
        return ["実行されたテストはありません。"]

    lines: list[str] = []
    for subpackage in sorted({case.subpackage for case in cases}):
        lines.append(f"### {subpackage}")
        lines.append("")
        lines.append("| テストメソッド名 | 結果 | 実行時間(秒) |")
        lines.append("|---|---|---|")
        for case in cases:
            if case.subpackage != subpackage:
                continue
            lines.append(f"| {case.method_name} | {_OUTCOME_LABELS[case.outcome]} | {case.duration_seconds:.3f} |")
        lines.append("")

    return lines
