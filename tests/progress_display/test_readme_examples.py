"""README.md に掲載する progress_display のサンプルコードがAPIと一致することを検証するテスト。"""

import io
import textwrap
import tomllib

from rich.console import Console

from python_util.progress_display import ProgressDisplay, ProgressDisplayConfig
from python_util.progress_display.config_loader import load_config


def _silent_console() -> Console:
    return Console(file=io.StringIO())


def test_readme_basic_multi_task_example():
    with ProgressDisplay(console=_silent_console()) as display:
        download_task = display.add_task("ダウンロード", total=100.0)
        convert_task = display.add_task("変換", total=50.0)

        display.update(download_task, advance=10.0)
        display.update(convert_task, completed=25.0)

        tasks = {t.id: t for t in display._progress.tasks}
        assert tasks[download_task].completed == 10.0
        assert tasks[convert_task].completed == 25.0


def test_readme_track_helper_example():
    processed = []
    with ProgressDisplay(console=_silent_console()) as display:
        for item in display.track(range(5), description="処理中"):
            processed.append(item)

    assert processed == list(range(5))


def test_readme_pyproject_toml_config_example(tmp_path):
    pyproject_text = textwrap.dedent("""
        [tool.python_util.progress_display]
        auto_remove_finished = true
        refresh_per_second = 5.0
        """)
    tomllib.loads(pyproject_text)
    (tmp_path / "pyproject.toml").write_text(pyproject_text)

    config = load_config(start_dir=tmp_path)

    assert config == ProgressDisplayConfig(auto_remove_finished=True, refresh_per_second=5.0)
