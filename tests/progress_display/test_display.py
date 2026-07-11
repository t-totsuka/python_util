"""ProgressDisplay の初期化・コンテキストマネージャによる開始/終了を検証するテスト。"""

import io

import pytest
from rich.console import Console
from rich.progress import TaskID, TextColumn

from python_util.progress_display.display import ProgressDisplay
from python_util.progress_display.exceptions import (
    DisplayNotStartedError,
    InvalidTotalError,
    UnknownTaskError,
)
from python_util.progress_display.types import ProgressDisplayConfig


def _silent_console() -> Console:
    return Console(file=io.StringIO())


def test_display_is_not_started_before_entering_context():
    display = ProgressDisplay(console=_silent_console())

    assert display._started is False


def test_context_manager_starts_display_on_enter():
    display = ProgressDisplay(console=_silent_console())

    with display as entered:
        assert entered is display
        assert display._started is True
        assert display._progress.live.is_started is True


def test_context_manager_stops_display_on_normal_exit():
    display = ProgressDisplay(console=_silent_console())

    with display:
        pass

    assert display._started is False
    assert display._progress.live.is_started is False


def test_context_manager_stops_display_when_exception_raised_in_block():
    display = ProgressDisplay(console=_silent_console())

    with pytest.raises(RuntimeError):
        with display:
            assert display._progress.live.is_started is True
            raise RuntimeError("boom")

    assert display._started is False
    assert display._progress.live.is_started is False


def test_init_accepts_custom_columns():
    custom_column = TextColumn("custom")

    display = ProgressDisplay(custom_column, console=_silent_console())

    assert custom_column in display._progress.columns


def test_init_without_columns_uses_default_columns():
    display = ProgressDisplay(console=_silent_console())

    assert len(display._progress.columns) > 0


def test_add_task_before_start_raises_display_not_started_error():
    display = ProgressDisplay(console=_silent_console())

    with pytest.raises(DisplayNotStartedError):
        display.add_task("task")


def test_add_task_with_zero_total_raises_invalid_total_error():
    with ProgressDisplay(console=_silent_console()) as display:
        with pytest.raises(InvalidTotalError):
            display.add_task("task", total=0)


def test_add_task_with_negative_total_raises_invalid_total_error():
    with ProgressDisplay(console=_silent_console()) as display:
        with pytest.raises(InvalidTotalError):
            display.add_task("task", total=-1)


def test_add_task_returns_unique_task_ids():
    with ProgressDisplay(console=_silent_console()) as display:
        first_id = display.add_task("first")
        second_id = display.add_task("second")

    assert first_id != second_id


def test_add_task_registers_description_total_and_completed():
    with ProgressDisplay(console=_silent_console()) as display:
        task_id = display.add_task("downloading", total=50.0, completed=10.0)

        task = next(t for t in display._progress.tasks if t.id == task_id)
        assert task.description == "downloading"
        assert task.total == 50.0
        assert task.completed == 10.0


def test_add_task_shows_multiple_tasks_in_single_display():
    with ProgressDisplay(console=_silent_console()) as display:
        first_id = display.add_task("first", total=10.0)
        second_id = display.add_task("second", total=20.0)

        visible_ids = {t.id for t in display._progress.tasks}
        assert first_id in visible_ids
        assert second_id in visible_ids


def test_add_task_completed_at_total_kept_visible_when_auto_remove_disabled():
    config = ProgressDisplayConfig(auto_remove_finished=False)
    with ProgressDisplay(config=config, console=_silent_console()) as display:
        task_id = display.add_task("done", total=10.0, completed=10.0)

        assert task_id in {t.id for t in display._progress.tasks}


def test_add_task_completed_at_total_auto_removed_when_enabled():
    config = ProgressDisplayConfig(auto_remove_finished=True)
    with ProgressDisplay(config=config, console=_silent_console()) as display:
        task_id = display.add_task("done", total=10.0, completed=10.0)

        assert task_id not in {t.id for t in display._progress.tasks}


def test_update_before_start_raises_display_not_started_error():
    display = ProgressDisplay(console=_silent_console())

    with pytest.raises(DisplayNotStartedError):
        display.update(TaskID(0), completed=1.0)


def test_update_unknown_task_raises_unknown_task_error():
    with ProgressDisplay(console=_silent_console()) as display:
        display.add_task("task", total=10.0)

        with pytest.raises(UnknownTaskError):
            display.update(TaskID(999), completed=1.0)


def test_update_with_absolute_completed_reflects_immediately():
    with ProgressDisplay(console=_silent_console()) as display:
        task_id = display.add_task("task", total=10.0)

        display.update(task_id, completed=4.0)

        task = next(t for t in display._progress.tasks if t.id == task_id)
        assert task.completed == 4.0


def test_update_with_advance_reflects_immediately():
    with ProgressDisplay(console=_silent_console()) as display:
        task_id = display.add_task("task", total=10.0, completed=2.0)

        display.update(task_id, advance=3.0)

        task = next(t for t in display._progress.tasks if t.id == task_id)
        assert task.completed == 5.0


def test_update_reaching_total_marks_finished():
    config = ProgressDisplayConfig(auto_remove_finished=False)
    with ProgressDisplay(config=config, console=_silent_console()) as display:
        task_id = display.add_task("task", total=10.0)

        display.update(task_id, completed=10.0)

        task = next(t for t in display._progress.tasks if t.id == task_id)
        assert task.finished is True


def test_update_reaching_total_kept_visible_when_auto_remove_disabled():
    config = ProgressDisplayConfig(auto_remove_finished=False)
    with ProgressDisplay(config=config, console=_silent_console()) as display:
        task_id = display.add_task("task", total=10.0)

        display.update(task_id, completed=10.0)

        assert task_id in {t.id for t in display._progress.tasks}


def test_update_reaching_total_auto_removed_when_enabled():
    config = ProgressDisplayConfig(auto_remove_finished=True)
    with ProgressDisplay(config=config, console=_silent_console()) as display:
        task_id = display.add_task("task", total=10.0)

        display.update(task_id, completed=10.0)

        assert task_id not in {t.id for t in display._progress.tasks}


def test_remove_task_before_start_raises_display_not_started_error():
    display = ProgressDisplay(console=_silent_console())

    with pytest.raises(DisplayNotStartedError):
        display.remove_task(TaskID(0))


def test_remove_task_unknown_task_raises_unknown_task_error():
    with ProgressDisplay(console=_silent_console()) as display:
        display.add_task("task", total=10.0)

        with pytest.raises(UnknownTaskError):
            display.remove_task(TaskID(999))


def test_remove_task_removes_task_from_display():
    with ProgressDisplay(console=_silent_console()) as display:
        task_id = display.add_task("task", total=10.0)

        display.remove_task(task_id)

        assert task_id not in {t.id for t in display._progress.tasks}


def test_remove_task_does_not_affect_other_tasks():
    with ProgressDisplay(console=_silent_console()) as display:
        first_id = display.add_task("first", total=10.0)
        second_id = display.add_task("second", total=10.0)

        display.remove_task(first_id)

        visible_ids = {t.id for t in display._progress.tasks}
        assert first_id not in visible_ids
        assert second_id in visible_ids


def test_track_before_start_raises_display_not_started_error():
    display = ProgressDisplay(console=_silent_console())

    with pytest.raises(DisplayNotStartedError):
        list(display.track([1, 2, 3]))


def test_track_yields_original_sequence_values():
    with ProgressDisplay(console=_silent_console()) as display:
        result = list(display.track(["a", "b", "c"]))

    assert result == ["a", "b", "c"]


def test_track_advances_progress_for_each_consumed_element():
    config = ProgressDisplayConfig(auto_remove_finished=False)
    with ProgressDisplay(config=config, console=_silent_console()) as display:
        task_id = None
        for _ in display.track([1, 2, 3]):
            if task_id is None:
                task_id = next(t.id for t in display._progress.tasks)

        completed = next(t.completed for t in display._progress.tasks if t.id == task_id)

    assert completed == 3.0


def test_track_uses_length_of_sequence_as_default_total():
    with ProgressDisplay(console=_silent_console()) as display:
        sequence = [1, 2, 3, 4]
        iterator = display.track(sequence)
        next(iterator)

        task = next(t for t in display._progress.tasks)
        assert task.total == 4.0

        list(iterator)


def test_track_with_explicit_total_overrides_default():
    with ProgressDisplay(console=_silent_console()) as display:
        iterator = display.track([1, 2, 3], total=10.0)
        next(iterator)

        task = next(t for t in display._progress.tasks)
        assert task.total == 10.0

        list(iterator)


def test_track_auto_removes_finished_task_when_enabled():
    config = ProgressDisplayConfig(auto_remove_finished=True)
    with ProgressDisplay(config=config, console=_silent_console()) as display:
        list(display.track([1, 2, 3]))

        assert len(display._progress.tasks) == 0


def test_add_task_with_non_string_description_raises_type_error():
    with ProgressDisplay(console=_silent_console()) as display:
        with pytest.raises(TypeError):
            display.add_task(123)


def test_add_task_with_non_numeric_total_raises_type_error():
    with ProgressDisplay(console=_silent_console()) as display:
        with pytest.raises(TypeError):
            display.add_task("task", total="10")


def test_add_task_with_non_numeric_completed_raises_type_error():
    with ProgressDisplay(console=_silent_console()) as display:
        with pytest.raises(TypeError):
            display.add_task("task", completed="0")


def test_update_with_non_task_id_raises_type_error():
    with ProgressDisplay(console=_silent_console()) as display:
        with pytest.raises(TypeError):
            display.update("not-a-task-id", completed=1.0)


def test_update_with_non_numeric_completed_raises_type_error():
    with ProgressDisplay(console=_silent_console()) as display:
        task_id = display.add_task("task", total=10.0)

        with pytest.raises(TypeError):
            display.update(task_id, completed="5")


def test_update_with_non_numeric_advance_raises_type_error():
    with ProgressDisplay(console=_silent_console()) as display:
        task_id = display.add_task("task", total=10.0)

        with pytest.raises(TypeError):
            display.update(task_id, advance="1")


def test_update_with_non_string_description_raises_type_error():
    with ProgressDisplay(console=_silent_console()) as display:
        task_id = display.add_task("task", total=10.0)

        with pytest.raises(TypeError):
            display.update(task_id, description=123)


def test_remove_task_with_non_task_id_raises_type_error():
    with ProgressDisplay(console=_silent_console()) as display:
        with pytest.raises(TypeError):
            display.remove_task("not-a-task-id")


def test_track_with_non_iterable_sequence_raises_type_error():
    with ProgressDisplay(console=_silent_console()) as display:
        with pytest.raises(TypeError):
            list(display.track(123))


def test_track_with_non_string_description_raises_type_error():
    with ProgressDisplay(console=_silent_console()) as display:
        with pytest.raises(TypeError):
            list(display.track([1, 2, 3], description=123))


def test_track_with_non_numeric_total_raises_type_error():
    with ProgressDisplay(console=_silent_console()) as display:
        with pytest.raises(TypeError):
            list(display.track([1, 2, 3], total="10"))
