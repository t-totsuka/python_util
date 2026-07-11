"""Handler Builder (`build_console_handler` / `build_file_handler`) を検証するテスト。"""

import logging

import pytest
from rich.logging import RichHandler

from python_util.logging.handlers import build_console_handler, build_file_handler


def test_build_console_handler_returns_rich_handler_with_level_and_formatter():
    handler = build_console_handler(logging.WARNING)

    assert isinstance(handler, RichHandler)
    assert handler.level == logging.WARNING
    assert handler.formatter is not None
    assert handler.formatter._fmt == "%(message)s"


def test_build_file_handler_creates_missing_directory(tmp_path):
    target = tmp_path / "logs" / "nested" / "app.log"

    handler = build_file_handler(target, logging.INFO)

    assert target.parent.is_dir()
    assert isinstance(handler, logging.FileHandler)
    assert handler.level == logging.INFO
    handler.close()


def test_build_file_handler_appends_and_formats_with_time_level_name_message(tmp_path):
    target = tmp_path / "app.log"

    handler = build_file_handler(target, logging.DEBUG)
    logger = logging.getLogger("test_handlers.append")
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    logger.info("hello world")
    handler.close()
    logger.removeHandler(handler)

    content = target.read_text()
    assert "hello world" in content
    assert "INFO" in content
    assert "test_handlers.append" in content


def test_build_file_handler_returns_none_and_warns_when_directory_creation_fails(
    tmp_path,
):
    blocked = tmp_path / "blocked"
    blocked.write_text("this is a file, not a directory")
    target = blocked / "app.log"

    with pytest.warns(UserWarning):
        handler = build_file_handler(target, logging.INFO)

    assert handler is None


def test_console_and_file_handlers_have_independent_levels(tmp_path):
    console_handler = build_console_handler(logging.ERROR)
    file_handler = build_file_handler(tmp_path / "app.log", logging.DEBUG)

    assert console_handler.level == logging.ERROR
    assert file_handler.level == logging.DEBUG
    file_handler.close()
