"""progress_display のトップレベル公開APIのみで一連の機能が完結することを検証するテスト。"""

import io

import pytest
from rich.console import Console

from python_util.progress_display import (
    DisplayNotStartedError,
    InvalidTotalError,
    ProgressDisplay,
    ProgressDisplayConfig,
    TaskID,
    UnknownTaskError,
)


def _silent_console() -> Console:
    return Console(file=io.StringIO())


def test_public_api_exports_expected_names():
    import python_util.progress_display as public_api

    assert set(public_api.__all__) == {
        "ProgressDisplay",
        "ProgressDisplayConfig",
        "TaskID",
        "UnknownTaskError",
        "InvalidTotalError",
        "DisplayNotStartedError",
    }


def test_full_workflow_using_only_top_level_imports():
    config = ProgressDisplayConfig(auto_remove_finished=True)

    with ProgressDisplay(config=config, console=_silent_console()) as display:
        task_id: TaskID = display.add_task("task", total=10.0)
        display.update(task_id, advance=5.0)
        display.update(task_id, completed=10.0)

        assert task_id not in {t.id for t in display._progress.tasks}

        other_id = display.add_task("other", total=10.0)
        display.remove_task(other_id)

        with pytest.raises(UnknownTaskError):
            display.remove_task(other_id)

        with pytest.raises(InvalidTotalError):
            display.add_task("invalid", total=0)

    not_started = ProgressDisplay(console=_silent_console())
    with pytest.raises(DisplayNotStartedError):
        not_started.add_task("task")
