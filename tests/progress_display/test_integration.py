"""複数タスクの同時進行・完了・自動非表示を通しで検証する結合テスト。"""

import io

import pytest
from rich.console import Console

from python_util.progress_display.display import ProgressDisplay
from python_util.progress_display.types import ProgressDisplayConfig


def _silent_console() -> Console:
    return Console(file=io.StringIO())


def test_multiple_tasks_progress_concurrently_and_finished_tasks_are_auto_removed():
    config = ProgressDisplayConfig(auto_remove_finished=True)

    with ProgressDisplay(config=config, console=_silent_console()) as display:
        task_a = display.add_task("A", total=5.0)
        task_b = display.add_task("B", total=3.0)
        task_c = display.add_task("C", total=2.0)

        visible_ids = {t.id for t in display._progress.tasks}
        assert {task_a, task_b, task_c} <= visible_ids

        display.update(task_a, advance=2.0)
        display.update(task_b, advance=1.0)
        display.update(task_c, completed=2.0)

        tasks_by_id = {t.id: t for t in display._progress.tasks}
        assert task_c not in tasks_by_id
        assert tasks_by_id[task_a].completed == 2.0
        assert tasks_by_id[task_b].completed == 1.0

        display.update(task_a, advance=3.0)
        display.update(task_b, advance=2.0)

        assert display._progress.tasks == []


def test_track_helper_advances_progress_step_by_step_while_iterating():
    config = ProgressDisplayConfig(auto_remove_finished=True)

    with ProgressDisplay(config=config, console=_silent_console()) as display:
        items = ["a", "b", "c"]
        tracked = display.track(items, description="loading")

        assert next(tracked) == "a"
        task = display._progress.tasks[0]
        assert task.description == "loading"
        assert task.total == 3.0
        assert task.completed == 0.0

        assert next(tracked) == "b"
        assert display._progress.tasks[0].completed == 1.0

        assert next(tracked) == "c"
        assert display._progress.tasks[0].completed == 2.0

        with pytest.raises(StopIteration):
            next(tracked)

        assert display._progress.tasks == []


def test_display_is_cleaned_up_when_exception_raised_inside_with_block():
    display = ProgressDisplay(console=_silent_console())

    class _SentinelError(Exception):
        pass

    with pytest.raises(_SentinelError):
        with display:
            display.add_task("A", total=5.0)
            assert display._progress.live.is_started
            raise _SentinelError("boom")

    assert not display._progress.live.is_started
    assert not display._started

    with display:
        assert display._progress.live.is_started
        task_id = display.add_task("B", total=2.0)
        display.update(task_id, advance=2.0)
        task = next(t for t in display._progress.tasks if t.id == task_id)
        assert task.finished
