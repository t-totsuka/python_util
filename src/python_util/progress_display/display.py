"""複数タスクの進捗を単一のコンソール表示領域で管理するファサード。"""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from operator import length_hint
from types import TracebackType

from rich.console import Console
from rich.progress import Progress, ProgressColumn, ProgressType, Task, TaskID

from python_util.progress_display.config_loader import load_config
from python_util.progress_display.exceptions import (
    DisplayNotStartedError,
    InvalidTotalError,
    UnknownTaskError,
)
from python_util.progress_display.types import ProgressDisplayConfig


def _check_type(value: object, expected: type | tuple[type, ...], name: str) -> None:
    if not isinstance(value, expected):
        raise TypeError(f"{name} の型が不正です: {type(value)!r}")


class ProgressDisplay:
    """複数の進捗タスクを単一のコンソール表示領域にまとめて管理・表示するファサード。"""

    def __init__(
        self,
        *columns: str | ProgressColumn,
        config: ProgressDisplayConfig | None = None,
        console: Console | None = None,
    ) -> None:
        self._config = config if config is not None else load_config()
        self._progress = Progress(
            *columns,
            console=console,
            refresh_per_second=self._config.refresh_per_second,
        )
        self._started = False

    def __enter__(self) -> ProgressDisplay:
        self._progress.start()
        self._started = True
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self._progress.stop()
        self._started = False

    def add_task(
        self,
        description: str,
        *,
        total: float = 100.0,
        completed: float = 0.0,
    ) -> TaskID:
        _check_type(description, str, "description")
        _check_type(total, (int, float), "total")
        _check_type(completed, (int, float), "completed")
        if not self._started:
            raise DisplayNotStartedError()
        if total <= 0:
            raise InvalidTotalError(total)

        task_id = self._progress.add_task(description, total=total, completed=completed)
        self._progress.update(task_id, completed=completed)
        self._remove_if_finished(task_id)
        return task_id

    def update(
        self,
        task_id: TaskID,
        *,
        completed: float | None = None,
        advance: float | None = None,
        description: str | None = None,
    ) -> None:
        _check_type(task_id, int, "task_id")
        if completed is not None:
            _check_type(completed, (int, float), "completed")
        if advance is not None:
            _check_type(advance, (int, float), "advance")
        if description is not None:
            _check_type(description, str, "description")
        if not self._started:
            raise DisplayNotStartedError()
        self._get_task(task_id)

        self._progress.update(task_id, completed=completed, advance=advance, description=description)
        self._remove_if_finished(task_id)

    def remove_task(self, task_id: TaskID) -> None:
        _check_type(task_id, int, "task_id")
        if not self._started:
            raise DisplayNotStartedError()
        self._get_task(task_id)

        self._progress.remove_task(task_id)

    def track(
        self,
        sequence: Iterable[ProgressType],
        *,
        description: str = "Working...",
        total: float | None = None,
    ) -> Iterator[ProgressType]:
        _check_type(sequence, Iterable, "sequence")
        _check_type(description, str, "description")
        if total is not None:
            _check_type(total, (int, float), "total")
        if not self._started:
            raise DisplayNotStartedError()
        if total is None:
            total = float(length_hint(sequence)) or None

        task_id = self._progress.add_task(description, total=total, completed=0)
        for value in sequence:
            yield value
            self.update(task_id, advance=1)

    def _get_task(self, task_id: TaskID) -> Task:
        for task in self._progress.tasks:
            if task.id == task_id:
                return task
        raise UnknownTaskError(task_id)

    def _remove_if_finished(self, task_id: TaskID) -> None:
        if not self._config.auto_remove_finished:
            return
        if self._get_task(task_id).finished:
            self._progress.remove_task(task_id)
