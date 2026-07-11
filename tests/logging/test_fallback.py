"""設定不備・環境不備時のフォールバック経路を、実ファイルシステムを用いて検証する結合テスト。"""

import logging
import textwrap
from pathlib import Path

import pytest
from rich.logging import RichHandler

import python_util.logging.factory as factory_module
from python_util.logging.factory import get_logger


def _write_pyproject(path: Path, content: str) -> None:
    (path / "pyproject.toml").write_text(textwrap.dedent(content))


@pytest.fixture(autouse=True)
def reset_factory_state():
    factory_module._reset_registry()
    yield
    factory_module._reset_registry()


def test_get_logger_falls_back_to_console_only_when_no_pyproject_toml(
    tmp_path, monkeypatch
):
    monkeypatch.chdir(tmp_path)

    logger = get_logger("moduleE")
    logger.info("should not raise")

    assert len(logger.handlers) == 1
    assert isinstance(logger.handlers[0], RichHandler)


def test_get_logger_falls_back_to_default_on_toml_syntax_error(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "pyproject.toml").write_text("this is not valid toml [[[")

    with pytest.warns(UserWarning):
        logger = get_logger("moduleF")
    logger.info("should not raise")

    assert len(logger.handlers) == 1
    assert isinstance(logger.handlers[0], RichHandler)


def test_get_logger_falls_back_to_default_on_unknown_level_string(
    tmp_path, monkeypatch
):
    monkeypatch.chdir(tmp_path)
    _write_pyproject(tmp_path, """
        [tool.python_util.logging]
        level = "NOT_A_LEVEL"
        """)

    with pytest.warns(UserWarning):
        logger = get_logger("moduleG")
    logger.info("should not raise")

    assert logger.handlers[0].level == logging.INFO


def test_get_logger_continues_with_console_only_when_directory_creation_fails(
    tmp_path, monkeypatch
):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "blocked").write_text("this is a file, not a directory")
    _write_pyproject(tmp_path, """
        [tool.python_util.logging]
        file = "blocked/app.log"
        """)

    with pytest.warns(UserWarning):
        logger = get_logger("moduleH")
    logger.info("should not raise despite directory creation failure")

    assert len(logger.handlers) == 1
    assert isinstance(logger.handlers[0], RichHandler)
