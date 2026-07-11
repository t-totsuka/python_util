"""Config Loader (`load_config`) を検証するテスト。"""

import textwrap
from pathlib import Path

import pytest

from python_util.progress_display.config_loader import load_config
from python_util.progress_display.types import ProgressDisplayConfig


def _write(path: Path, content: str) -> None:
    path.write_text(textwrap.dedent(content))


def test_単体正常系_load_configが_pyproject_tomlが見つからない場合_デフォルト設定を返す(tmp_path):
    start_dir = tmp_path / "no_pyproject"
    start_dir.mkdir()

    config = load_config(start_dir=start_dir)

    assert config == ProgressDisplayConfig()


def test_単体正常系_load_configが_設定テーブルが存在しない場合_デフォルト設定を返す(tmp_path):
    _write(tmp_path / "pyproject.toml", """
        [project]
        name = "sample"
        """)

    config = load_config(start_dir=tmp_path)

    assert config == ProgressDisplayConfig()


def test_単体正常系_load_configが_完全な設定テーブルを受け取った場合_値を解析して返す(tmp_path):
    _write(tmp_path / "pyproject.toml", """
        [tool.python_util.progress_display]
        auto_remove_finished = true
        refresh_per_second = 5.0
        """)

    config = load_config(start_dir=tmp_path)

    assert config.auto_remove_finished is True
    assert config.refresh_per_second == 5.0


def test_異常系_load_configが_TOML構文エラーを含む場合_警告を出しデフォルト設定にフォールバックする(tmp_path):
    _write(tmp_path / "pyproject.toml", "this is not valid toml [[[")

    with pytest.warns(UserWarning):
        config = load_config(start_dir=tmp_path)

    assert config == ProgressDisplayConfig()


def test_異常系_load_configが_refresh_per_secondに0を指定された場合_警告を出しデフォルト設定にフォールバックする(tmp_path):
    _write(tmp_path / "pyproject.toml", """
        [tool.python_util.progress_display]
        refresh_per_second = 0
        """)

    with pytest.warns(UserWarning):
        config = load_config(start_dir=tmp_path)

    assert config == ProgressDisplayConfig()


def test_異常系_load_configが_refresh_per_secondに負数を指定された場合_警告を出しデフォルト設定にフォールバックする(tmp_path):
    _write(tmp_path / "pyproject.toml", """
        [tool.python_util.progress_display]
        refresh_per_second = -1.0
        """)

    with pytest.warns(UserWarning):
        config = load_config(start_dir=tmp_path)

    assert config == ProgressDisplayConfig()


def test_異常系_load_configが_auto_remove_finishedに不正な型を指定された場合_警告を出しデフォルト設定にフォールバックする(tmp_path):
    _write(tmp_path / "pyproject.toml", """
        [tool.python_util.progress_display]
        auto_remove_finished = "yes"
        """)

    with pytest.warns(UserWarning):
        config = load_config(start_dir=tmp_path)

    assert config == ProgressDisplayConfig()


def test_単体正常系_load_configが_開始ディレクトリにpyproject_tomlがない場合_親ディレクトリを探索して設定を読み込む(tmp_path):
    _write(tmp_path / "pyproject.toml", """
        [tool.python_util.progress_display]
        auto_remove_finished = true
        """)
    child_dir = tmp_path / "src" / "app"
    child_dir.mkdir(parents=True)

    config = load_config(start_dir=child_dir)

    assert config.auto_remove_finished is True


def test_境界_load_configが_複数階層にpyproject_tomlが存在する場合_最初に見つかったファイルのみを考慮する(tmp_path):
    _write(tmp_path / "pyproject.toml", """
        [tool.python_util.progress_display]
        auto_remove_finished = true
        """)
    child_dir = tmp_path / "child"
    child_dir.mkdir()
    _write(child_dir / "pyproject.toml", """
        [project]
        name = "child"
        """)

    config = load_config(start_dir=child_dir)

    assert config == ProgressDisplayConfig()


def test_単体正常系_load_configが_start_dirを省略された場合_カレントディレクトリを起点に探索する(monkeypatch, tmp_path):
    _write(tmp_path / "pyproject.toml", """
        [tool.python_util.progress_display]
        auto_remove_finished = true
        """)
    monkeypatch.chdir(tmp_path)

    config = load_config()

    assert config.auto_remove_finished is True
