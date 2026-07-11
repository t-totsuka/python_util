"""Config Loader (`load_config`) を検証するテスト。"""

import textwrap
from pathlib import Path

import pytest

from python_util.progress_display.config_loader import load_config
from python_util.progress_display.types import ProgressDisplayConfig


def _write(path: Path, content: str) -> None:
    path.write_text(textwrap.dedent(content))


def test_load_config_returns_default_when_no_pyproject_toml_found(tmp_path):
    start_dir = tmp_path / "no_pyproject"
    start_dir.mkdir()

    config = load_config(start_dir=start_dir)

    assert config == ProgressDisplayConfig()


def test_load_config_returns_default_when_table_absent(tmp_path):
    _write(tmp_path / "pyproject.toml", """
        [project]
        name = "sample"
        """)

    config = load_config(start_dir=tmp_path)

    assert config == ProgressDisplayConfig()


def test_load_config_parses_full_table(tmp_path):
    _write(tmp_path / "pyproject.toml", """
        [tool.python_util.progress_display]
        auto_remove_finished = true
        refresh_per_second = 5.0
        """)

    config = load_config(start_dir=tmp_path)

    assert config.auto_remove_finished is True
    assert config.refresh_per_second == 5.0


def test_load_config_falls_back_on_toml_syntax_error(tmp_path):
    _write(tmp_path / "pyproject.toml", "this is not valid toml [[[")

    with pytest.warns(UserWarning):
        config = load_config(start_dir=tmp_path)

    assert config == ProgressDisplayConfig()


def test_load_config_falls_back_on_invalid_refresh_per_second(tmp_path):
    _write(tmp_path / "pyproject.toml", """
        [tool.python_util.progress_display]
        refresh_per_second = 0
        """)

    with pytest.warns(UserWarning):
        config = load_config(start_dir=tmp_path)

    assert config == ProgressDisplayConfig()


def test_load_config_falls_back_on_negative_refresh_per_second(tmp_path):
    _write(tmp_path / "pyproject.toml", """
        [tool.python_util.progress_display]
        refresh_per_second = -1.0
        """)

    with pytest.warns(UserWarning):
        config = load_config(start_dir=tmp_path)

    assert config == ProgressDisplayConfig()


def test_load_config_falls_back_on_invalid_type(tmp_path):
    _write(tmp_path / "pyproject.toml", """
        [tool.python_util.progress_display]
        auto_remove_finished = "yes"
        """)

    with pytest.warns(UserWarning):
        config = load_config(start_dir=tmp_path)

    assert config == ProgressDisplayConfig()


def test_load_config_searches_parent_directories(tmp_path):
    _write(tmp_path / "pyproject.toml", """
        [tool.python_util.progress_display]
        auto_remove_finished = true
        """)
    child_dir = tmp_path / "src" / "app"
    child_dir.mkdir(parents=True)

    config = load_config(start_dir=child_dir)

    assert config.auto_remove_finished is True


def test_load_config_only_considers_first_found_pyproject(tmp_path):
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


def test_load_config_defaults_start_dir_to_cwd(monkeypatch, tmp_path):
    _write(tmp_path / "pyproject.toml", """
        [tool.python_util.progress_display]
        auto_remove_finished = true
        """)
    monkeypatch.chdir(tmp_path)

    config = load_config()

    assert config.auto_remove_finished is True
