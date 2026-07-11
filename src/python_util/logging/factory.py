"""get_logger 実装と設定済みロガー名のレジストリ管理。"""

from __future__ import annotations

import inspect
import logging
import threading

from python_util.logging.config_loader import load_config, resolve_logger_override
from python_util.logging.handlers import build_console_handler, build_file_handler
from python_util.logging.types import LoggingConfig

_configured_names: set[str] = set()
_config_cache: LoggingConfig | None = None
_registry_lock = threading.Lock()


def get_logger(name: str | None = None) -> logging.Logger:
    resolved_name = name if name else _caller_module_name()
    logger = logging.getLogger(resolved_name)
    with _registry_lock:
        if resolved_name not in _configured_names:
            _configure_logger(logger, resolved_name)
            _configured_names.add(resolved_name)
    return logger


def _caller_module_name() -> str:
    caller_frame = inspect.stack()[2].frame
    return caller_frame.f_globals.get("__name__", "__main__")


def _get_config() -> LoggingConfig:
    global _config_cache
    if _config_cache is None:
        _config_cache = load_config()
    return _config_cache


def _configure_logger(logger: logging.Logger, name: str) -> None:
    config = _get_config()
    override = resolve_logger_override(config, name)

    default_level = (
        override.level if override and override.level is not None else config.default_level
    )
    console_level = (
        override.console_level
        if override and override.console_level is not None
        else config.console_level if config.console_level is not None else default_level
    )
    file_level = config.file_level if config.file_level is not None else default_level
    file_path = (
        override.file_path if override and override.file_path is not None else config.file_path
    )

    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    if config.console_enabled:
        logger.addHandler(build_console_handler(console_level))

    if file_path is not None:
        file_handler = build_file_handler(file_path, file_level)
        if file_handler is not None:
            logger.addHandler(file_handler)


def _reset_registry() -> None:
    """テスト用: レジストリと設定キャッシュをリセットする。"""
    global _config_cache
    for name in list(_configured_names):
        logger = logging.getLogger(name)
        for handler in list(logger.handlers):
            logger.removeHandler(handler)
            handler.close()
    _configured_names.clear()
    _config_cache = None
