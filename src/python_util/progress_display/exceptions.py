"""progress_display パッケージ固有の例外定義。"""

from __future__ import annotations


class UnknownTaskError(ValueError):
    """管理対象外のタスク識別子に対して操作が要求された場合に送出される。"""

    def __init__(self, task_id: object) -> None:
        super().__init__(f"管理対象外のタスク識別子です: {task_id!r}")


class InvalidTotalError(ValueError):
    """タスクの総量(total)に0以下の値が指定された場合に送出される。"""

    def __init__(self, total: object) -> None:
        super().__init__(f"不正な総量(total)が指定されました: {total!r}")


class DisplayNotStartedError(ValueError):
    """ProgressDisplayが開始されていない状態でタスク操作が要求された場合に送出される。"""

    def __init__(self) -> None:
        super().__init__("ProgressDisplayが開始されていません。with文で開始してから操作してください")


class _InvalidProgressDisplayConfig(Exception):
    """progress_display 設定テーブルの解析・値検証に失敗したことを示す内部例外。"""
