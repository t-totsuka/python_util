"""get_logger 実装と設定済みロガー名のレジストリ管理。"""

from __future__ import annotations

import inspect
import logging
import threading
from pathlib import Path

from python_util.logging.config_loader import load_config, resolve_logger_override
from python_util.logging.handlers import build_console_handler, build_file_handler
from python_util.logging.types import LoggingConfig

_configured_names: set[str] = set()
_config_cache: LoggingConfig | None = None
_file_handler_cache: dict[Path, logging.Handler] = {}
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
        file_handler = _get_file_handler(file_path, file_level, config)
        if file_handler is not None:
            logger.addHandler(file_handler)


def _get_file_handler(
    file_path: Path, file_level: int, config: LoggingConfig
) -> logging.Handler | None:
    """解決済み出力パス単位でファイルハンドラをキャッシュ・共有する。

    同一パスに複数の`TimedRotatingFileHandler`インスタンスが載ると、
    ローテーション実行後に後続インスタンスのストリームが退避済みファイルを
    指し続け当日ログが前日の退避ファイルへ混入するため、この共有は正しさの
    要件である（design.md Logger Factory参照）。
    """
    cached_handler = _file_handler_cache.get(file_path)
    if cached_handler is not None:
        return cached_handler

    file_handler = build_file_handler(
        file_path,
        file_level,
        rotation_enabled=config.rotation_enabled,
        retention_days=config.retention_days,
    )
    if file_handler is not None:
        _file_handler_cache[file_path] = file_handler
    return file_handler


def _reset_registry() -> None:
    """テスト用: レジストリ・設定キャッシュ・ファイルハンドラキャッシュをリセットする。"""
    global _config_cache
    cached_handlers = set(_file_handler_cache.values())
    for name in list(_configured_names):
        logger = logging.getLogger(name)
        for handler in list(logger.handlers):
            logger.removeHandler(handler)
            if handler not in cached_handlers:
                handler.close()
    for handler in cached_handlers:
        handler.close()
    _configured_names.clear()
    _file_handler_cache.clear()
    _config_cache = None
