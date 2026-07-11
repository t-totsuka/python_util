"""LoggingConfig / LoggerOverride の値オブジェクトを検証するテスト。"""

import dataclasses
import logging as std_logging

import pytest

from python_util.logging.types import LoggerOverride, LoggingConfig


def test_単体正常系_LoggingConfigが_デフォルト生成された場合_既定値を保持する():
    config = LoggingConfig()

    assert config.default_level == std_logging.INFO
    assert config.console_enabled is True
    assert config.console_level is None
    assert config.file_path is None
    assert config.file_level is None
    assert config.loggers == {}


def test_異常系_LoggingConfigが_属性変更を試みられた場合_FrozenInstanceErrorを送出する():
    config = LoggingConfig()

    with pytest.raises(dataclasses.FrozenInstanceError):
        config.default_level = std_logging.DEBUG  # type: ignore[misc]


def test_単体正常系_LoggingConfigが_フィールド定義された場合_明示的な型ヒントを持つ():
    hints = {f.name: f.type for f in dataclasses.fields(LoggingConfig)}

    assert hints == {
        "default_level": "int",
        "console_enabled": "bool",
        "console_level": "int | None",
        "file_path": "Path | None",
        "file_level": "int | None",
        "loggers": "dict[str, LoggerOverride]",
    }


def test_単体正常系_LoggerOverrideが_デフォルト生成された場合_既定値を保持する():
    override = LoggerOverride()

    assert override.file_path is None
    assert override.level is None
    assert override.console_level is None


def test_異常系_LoggerOverrideが_属性変更を試みられた場合_FrozenInstanceErrorを送出する():
    override = LoggerOverride()

    with pytest.raises(dataclasses.FrozenInstanceError):
        override.level = std_logging.DEBUG  # type: ignore[misc]


def test_単体正常系_LoggerOverrideが_フィールド定義された場合_明示的な型ヒントを持つ():
    hints = {f.name: f.type for f in dataclasses.fields(LoggerOverride)}

    assert hints == {
        "file_path": "Path | None",
        "level": "int | None",
        "console_level": "int | None",
    }
