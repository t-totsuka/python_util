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


def test_単体正常系_ProgressDisplayが_コンテキストに入る前の場合_開始状態でない():
    display = ProgressDisplay(console=_silent_console())

    assert display._started is False


def test_単体正常系_ProgressDisplayが_withブロックに入った場合_表示を開始する():
    display = ProgressDisplay(console=_silent_console())

    with display as entered:
        assert entered is display
        assert display._started is True
        assert display._progress.live.is_started is True


def test_単体正常系_ProgressDisplayが_withブロックを正常に抜けた場合_表示を停止する():
    display = ProgressDisplay(console=_silent_console())

    with display:
        pass

    assert display._started is False
    assert display._progress.live.is_started is False


def test_異常系_ProgressDisplayが_withブロック内で例外が発生した場合_表示を停止する():
    display = ProgressDisplay(console=_silent_console())

    with pytest.raises(RuntimeError):
        with display:
            assert display._progress.live.is_started is True
            raise RuntimeError("boom")

    assert display._started is False
    assert display._progress.live.is_started is False


def test_単体正常系_ProgressDisplayが_カスタムカラムを渡された場合_カラムを保持する():
    custom_column = TextColumn("custom")

    display = ProgressDisplay(custom_column, console=_silent_console())

    assert custom_column in display._progress.columns


def test_単体正常系_ProgressDisplayが_カラムを指定されなかった場合_デフォルトカラムを使用する():
    display = ProgressDisplay(console=_silent_console())

    assert len(display._progress.columns) > 0


def test_異常系_add_taskが_表示開始前に呼び出された場合_DisplayNotStartedErrorを送出する():
    display = ProgressDisplay(console=_silent_console())

    with pytest.raises(DisplayNotStartedError):
        display.add_task("task")


def test_異常系_add_taskが_totalに0を指定された場合_InvalidTotalErrorを送出する():
    with ProgressDisplay(console=_silent_console()) as display:
        with pytest.raises(InvalidTotalError):
            display.add_task("task", total=0)


def test_異常系_add_taskが_totalに負数を指定された場合_InvalidTotalErrorを送出する():
    with ProgressDisplay(console=_silent_console()) as display:
        with pytest.raises(InvalidTotalError):
            display.add_task("task", total=-1)


def test_単体正常系_add_taskが_複数回呼び出された場合_一意なタスクIDを返す():
    with ProgressDisplay(console=_silent_console()) as display:
        first_id = display.add_task("first")
        second_id = display.add_task("second")

    assert first_id != second_id


def test_単体正常系_add_taskが_説明文とtotalとcompletedを指定された場合_タスクへ登録する():
    with ProgressDisplay(console=_silent_console()) as display:
        task_id = display.add_task("downloading", total=50.0, completed=10.0)

        task = next(t for t in display._progress.tasks if t.id == task_id)
        assert task.description == "downloading"
        assert task.total == 50.0
        assert task.completed == 10.0


def test_単体正常系_add_taskが_複数回呼び出された場合_単一の表示に複数タスクを表示する():
    with ProgressDisplay(console=_silent_console()) as display:
        first_id = display.add_task("first", total=10.0)
        second_id = display.add_task("second", total=20.0)

        visible_ids = {t.id for t in display._progress.tasks}
        assert first_id in visible_ids
        assert second_id in visible_ids


def test_単体正常系_add_taskが_completedがtotalに到達しauto_remove_finishedが無効な場合_タスクを表示し続ける():
    config = ProgressDisplayConfig(auto_remove_finished=False)
    with ProgressDisplay(config=config, console=_silent_console()) as display:
        task_id = display.add_task("done", total=10.0, completed=10.0)

        assert task_id in {t.id for t in display._progress.tasks}


def test_単体正常系_add_taskが_completedがtotalに到達しauto_remove_finishedが有効な場合_タスクを自動的に削除する():
    config = ProgressDisplayConfig(auto_remove_finished=True)
    with ProgressDisplay(config=config, console=_silent_console()) as display:
        task_id = display.add_task("done", total=10.0, completed=10.0)

        assert task_id not in {t.id for t in display._progress.tasks}


def test_異常系_updateが_表示開始前に呼び出された場合_DisplayNotStartedErrorを送出する():
    display = ProgressDisplay(console=_silent_console())

    with pytest.raises(DisplayNotStartedError):
        display.update(TaskID(0), completed=1.0)


def test_異常系_updateが_未知のタスクIDを指定された場合_UnknownTaskErrorを送出する():
    with ProgressDisplay(console=_silent_console()) as display:
        display.add_task("task", total=10.0)

        with pytest.raises(UnknownTaskError):
            display.update(TaskID(999), completed=1.0)


def test_単体正常系_updateが_completedを絶対値で指定された場合_即座に反映する():
    with ProgressDisplay(console=_silent_console()) as display:
        task_id = display.add_task("task", total=10.0)

        display.update(task_id, completed=4.0)

        task = next(t for t in display._progress.tasks if t.id == task_id)
        assert task.completed == 4.0


def test_単体正常系_updateが_advanceを指定された場合_即座に加算して反映する():
    with ProgressDisplay(console=_silent_console()) as display:
        task_id = display.add_task("task", total=10.0, completed=2.0)

        display.update(task_id, advance=3.0)

        task = next(t for t in display._progress.tasks if t.id == task_id)
        assert task.completed == 5.0


def test_単体正常系_updateが_completedがtotalに到達した場合_タスクをfinished状態にする():
    config = ProgressDisplayConfig(auto_remove_finished=False)
    with ProgressDisplay(config=config, console=_silent_console()) as display:
        task_id = display.add_task("task", total=10.0)

        display.update(task_id, completed=10.0)

        task = next(t for t in display._progress.tasks if t.id == task_id)
        assert task.finished is True


def test_単体正常系_updateが_completedがtotalに到達しauto_remove_finishedが無効な場合_タスクを表示し続ける():
    config = ProgressDisplayConfig(auto_remove_finished=False)
    with ProgressDisplay(config=config, console=_silent_console()) as display:
        task_id = display.add_task("task", total=10.0)

        display.update(task_id, completed=10.0)

        assert task_id in {t.id for t in display._progress.tasks}


def test_単体正常系_updateが_completedがtotalに到達しauto_remove_finishedが有効な場合_タスクを自動的に削除する():
    config = ProgressDisplayConfig(auto_remove_finished=True)
    with ProgressDisplay(config=config, console=_silent_console()) as display:
        task_id = display.add_task("task", total=10.0)

        display.update(task_id, completed=10.0)

        assert task_id not in {t.id for t in display._progress.tasks}


def test_異常系_remove_taskが_表示開始前に呼び出された場合_DisplayNotStartedErrorを送出する():
    display = ProgressDisplay(console=_silent_console())

    with pytest.raises(DisplayNotStartedError):
        display.remove_task(TaskID(0))


def test_異常系_remove_taskが_未知のタスクIDを指定された場合_UnknownTaskErrorを送出する():
    with ProgressDisplay(console=_silent_console()) as display:
        display.add_task("task", total=10.0)

        with pytest.raises(UnknownTaskError):
            display.remove_task(TaskID(999))


def test_単体正常系_remove_taskが_既知のタスクIDを指定された場合_表示からタスクを削除する():
    with ProgressDisplay(console=_silent_console()) as display:
        task_id = display.add_task("task", total=10.0)

        display.remove_task(task_id)

        assert task_id not in {t.id for t in display._progress.tasks}


def test_単体正常系_remove_taskが_一つのタスクを削除した場合_他のタスクに影響しない():
    with ProgressDisplay(console=_silent_console()) as display:
        first_id = display.add_task("first", total=10.0)
        second_id = display.add_task("second", total=10.0)

        display.remove_task(first_id)

        visible_ids = {t.id for t in display._progress.tasks}
        assert first_id not in visible_ids
        assert second_id in visible_ids


def test_異常系_trackが_表示開始前に呼び出された場合_DisplayNotStartedErrorを送出する():
    display = ProgressDisplay(console=_silent_console())

    with pytest.raises(DisplayNotStartedError):
        list(display.track([1, 2, 3]))


def test_単体正常系_trackが_シーケンスを渡された場合_元の値をそのまま順に返す():
    with ProgressDisplay(console=_silent_console()) as display:
        result = list(display.track(["a", "b", "c"]))

    assert result == ["a", "b", "c"]


def test_単体正常系_trackが_要素を消費するたびに_進捗を1ずつ進める():
    config = ProgressDisplayConfig(auto_remove_finished=False)
    with ProgressDisplay(config=config, console=_silent_console()) as display:
        task_id = None
        for _ in display.track([1, 2, 3]):
            if task_id is None:
                task_id = next(t.id for t in display._progress.tasks)

        completed = next(t.completed for t in display._progress.tasks if t.id == task_id)

    assert completed == 3.0


def test_単体正常系_trackが_totalを指定されなかった場合_シーケンスの長さをデフォルトのtotalとして使用する():
    with ProgressDisplay(console=_silent_console()) as display:
        sequence = [1, 2, 3, 4]
        iterator = display.track(sequence)
        next(iterator)

        task = next(t for t in display._progress.tasks)
        assert task.total == 4.0

        list(iterator)


def test_単体正常系_trackが_totalを明示的に指定された場合_デフォルト値より優先する():
    with ProgressDisplay(console=_silent_console()) as display:
        iterator = display.track([1, 2, 3], total=10.0)
        next(iterator)

        task = next(t for t in display._progress.tasks)
        assert task.total == 10.0

        list(iterator)


def test_単体正常系_trackが_auto_remove_finishedが有効な場合_完了後にタスクを自動的に削除する():
    config = ProgressDisplayConfig(auto_remove_finished=True)
    with ProgressDisplay(config=config, console=_silent_console()) as display:
        list(display.track([1, 2, 3]))

        assert len(display._progress.tasks) == 0


def test_異常系_add_taskが_descriptionに文字列以外を指定された場合_TypeErrorを送出する():
    with ProgressDisplay(console=_silent_console()) as display:
        with pytest.raises(TypeError):
            display.add_task(123)


def test_異常系_add_taskが_totalに数値以外を指定された場合_TypeErrorを送出する():
    with ProgressDisplay(console=_silent_console()) as display:
        with pytest.raises(TypeError):
            display.add_task("task", total="10")


def test_異常系_add_taskが_completedに数値以外を指定された場合_TypeErrorを送出する():
    with ProgressDisplay(console=_silent_console()) as display:
        with pytest.raises(TypeError):
            display.add_task("task", completed="0")


def test_異常系_updateが_task_idにTaskID以外を指定された場合_TypeErrorを送出する():
    with ProgressDisplay(console=_silent_console()) as display:
        with pytest.raises(TypeError):
            display.update("not-a-task-id", completed=1.0)


def test_異常系_updateが_completedに数値以外を指定された場合_TypeErrorを送出する():
    with ProgressDisplay(console=_silent_console()) as display:
        task_id = display.add_task("task", total=10.0)

        with pytest.raises(TypeError):
            display.update(task_id, completed="5")


def test_異常系_updateが_advanceに数値以外を指定された場合_TypeErrorを送出する():
    with ProgressDisplay(console=_silent_console()) as display:
        task_id = display.add_task("task", total=10.0)

        with pytest.raises(TypeError):
            display.update(task_id, advance="1")


def test_異常系_updateが_descriptionに文字列以外を指定された場合_TypeErrorを送出する():
    with ProgressDisplay(console=_silent_console()) as display:
        task_id = display.add_task("task", total=10.0)

        with pytest.raises(TypeError):
            display.update(task_id, description=123)


def test_異常系_remove_taskが_task_idにTaskID以外を指定された場合_TypeErrorを送出する():
    with ProgressDisplay(console=_silent_console()) as display:
        with pytest.raises(TypeError):
            display.remove_task("not-a-task-id")


def test_異常系_trackが_イテラブルでない値を指定された場合_TypeErrorを送出する():
    with ProgressDisplay(console=_silent_console()) as display:
        with pytest.raises(TypeError):
            list(display.track(123))


def test_異常系_trackが_descriptionに文字列以外を指定された場合_TypeErrorを送出する():
    with ProgressDisplay(console=_silent_console()) as display:
        with pytest.raises(TypeError):
            list(display.track([1, 2, 3], description=123))


def test_異常系_trackが_totalに数値以外を指定された場合_TypeErrorを送出する():
    with ProgressDisplay(console=_silent_console()) as display:
        with pytest.raises(TypeError):
            list(display.track([1, 2, 3], total="10"))
