"""LoggingConfig / LoggerOverride の値オブジェクトを検証するテスト。"""

import dataclasses
import logging as std_logging

import pytest

from python_util.logging.types import LoggerOverride, LoggingConfig


def test_logging_config_default_values():
    config = LoggingConfig()

    assert config.default_level == std_logging.INFO
    assert config.console_enabled is True
    assert config.console_level is None
    assert config.file_path is None
    assert config.file_level is None
    assert config.loggers == {}


def test_logging_config_is_frozen():
    config = LoggingConfig()

    with pytest.raises(dataclasses.FrozenInstanceError):
        config.default_level = std_logging.DEBUG  # type: ignore[misc]


def test_logging_config_fields_have_explicit_types():
    hints = {f.name: f.type for f in dataclasses.fields(LoggingConfig)}

    assert hints == {
        "default_level": "int",
        "console_enabled": "bool",
        "console_level": "int | None",
        "file_path": "Path | None",
        "file_level": "int | None",
        "loggers": "dict[str, LoggerOverride]",
    }


def test_logger_override_default_values():
    override = LoggerOverride()

    assert override.file_path is None
    assert override.level is None
    assert override.console_level is None


def test_logger_override_is_frozen():
    override = LoggerOverride()

    with pytest.raises(dataclasses.FrozenInstanceError):
        override.level = std_logging.DEBUG  # type: ignore[misc]


def test_logger_override_fields_have_explicit_types():
    hints = {f.name: f.type for f in dataclasses.fields(LoggerOverride)}

    assert hints == {
        "file_path": "Path | None",
        "level": "int | None",
        "console_level": "int | None",
    }
