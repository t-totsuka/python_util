"""Config Loader (`load_config` / `resolve_logger_override`) を検証するテスト。"""

import logging
import textwrap
from pathlib import Path

import pytest

from python_util.logging.config_loader import load_config, resolve_logger_override
from python_util.logging.types import LoggerOverride, LoggingConfig


def _write(path: Path, content: str) -> None:
    path.write_text(textwrap.dedent(content))


def test_load_config_returns_default_when_no_pyproject_toml_found(tmp_path):
    start_dir = tmp_path / "no_pyproject"
    start_dir.mkdir()

    config = load_config(start_dir=start_dir)

    assert config == LoggingConfig()


def test_load_config_returns_default_when_table_absent(tmp_path):
    _write(tmp_path / "pyproject.toml", """
        [project]
        name = "sample"
        """)

    config = load_config(start_dir=tmp_path)

    assert config == LoggingConfig()


def test_load_config_parses_full_table(tmp_path):
    _write(tmp_path / "pyproject.toml", """
        [tool.python_util.logging]
        level = "DEBUG"
        file = "logs/app.log"
        file_level = "WARNING"

        [tool.python_util.logging.console]
        enabled = false
        level = "ERROR"

        [tool.python_util.logging.loggers."myapp.worker"]
        file = "logs/worker.log"
        level = "INFO"
        """)

    config = load_config(start_dir=tmp_path)

    assert config.default_level == logging.DEBUG
    assert config.file_path == Path("logs/app.log")
    assert config.file_level == logging.WARNING
    assert config.console_enabled is False
    assert config.console_level == logging.ERROR
    assert config.loggers == {
        "myapp.worker": LoggerOverride(
            file_path=Path("logs/worker.log"), level=logging.INFO
        )
    }


def test_load_config_falls_back_on_toml_syntax_error(tmp_path):
    _write(tmp_path / "pyproject.toml", "this is not valid toml [[[")

    with pytest.warns(UserWarning):
        config = load_config(start_dir=tmp_path)

    assert config == LoggingConfig()


def test_load_config_falls_back_on_unknown_level_string(tmp_path):
    _write(tmp_path / "pyproject.toml", """
        [tool.python_util.logging]
        level = "NOT_A_LEVEL"
        """)

    with pytest.warns(UserWarning):
        config = load_config(start_dir=tmp_path)

    assert config == LoggingConfig()


def test_load_config_searches_parent_directories(tmp_path):
    _write(tmp_path / "pyproject.toml", """
        [tool.python_util.logging]
        level = "ERROR"
        """)
    child_dir = tmp_path / "src" / "app"
    child_dir.mkdir(parents=True)

    config = load_config(start_dir=child_dir)

    assert config.default_level == logging.ERROR


def test_load_config_only_considers_first_found_pyproject(tmp_path):
    _write(tmp_path / "pyproject.toml", """
        [tool.python_util.logging]
        level = "ERROR"
        """)
    child_dir = tmp_path / "child"
    child_dir.mkdir()
    _write(child_dir / "pyproject.toml", """
        [project]
        name = "child"
        """)

    config = load_config(start_dir=child_dir)

    assert config == LoggingConfig()


def test_resolve_logger_override_longest_prefix_match():
    config = LoggingConfig(
        loggers={
            "myapp": LoggerOverride(level=logging.WARNING),
            "myapp.worker": LoggerOverride(level=logging.DEBUG),
        }
    )

    override = resolve_logger_override(config, "myapp.worker.io")

    assert override == LoggerOverride(level=logging.DEBUG)


def test_resolve_logger_override_no_match_returns_none():
    config = LoggingConfig(loggers={"myapp": LoggerOverride(level=logging.WARNING)})

    override = resolve_logger_override(config, "otherapp.io")

    assert override is None
