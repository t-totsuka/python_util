"""呼び出し側 pyproject.toml の探索・解析。"""

from __future__ import annotations

import logging
import tomllib
import warnings
from pathlib import Path
from typing import Any

from python_util.logging.types import LoggerOverride, LoggingConfig

_LEVEL_NAMES: dict[str, int] = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}


class _InvalidLoggingConfig(Exception):
    """ロギング設定テーブルの解析に失敗したことを示す内部例外。"""


def load_config(start_dir: Path | None = None) -> LoggingConfig:
    base_dir = start_dir if start_dir is not None else Path.cwd()
    pyproject_path = _find_pyproject_toml(base_dir)
    if pyproject_path is None:
        return LoggingConfig()

    try:
        data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    except (tomllib.TOMLDecodeError, UnicodeDecodeError) as exc:
        warnings.warn(f"{pyproject_path} の解析に失敗しました: {exc}")
        return LoggingConfig()

    table = data.get("tool", {}).get("python_util", {}).get("logging")
    if table is None:
        return LoggingConfig()

    try:
        return _parse_logging_table(table)
    except _InvalidLoggingConfig as exc:
        warnings.warn(f"{pyproject_path} の [tool.python_util.logging] が不正です: {exc}")
        return LoggingConfig()


def resolve_logger_override(config: LoggingConfig, name: str) -> LoggerOverride | None:
    best_match: str | None = None
    for key in config.loggers:
        if name == key or name.startswith(f"{key}."):
            if best_match is None or len(key) > len(best_match):
                best_match = key
    if best_match is None:
        return None
    return config.loggers[best_match]


def _find_pyproject_toml(start_dir: Path) -> Path | None:
    current = start_dir
    while True:
        candidate = current / "pyproject.toml"
        if candidate.is_file():
            return candidate
        if current.parent == current:
            return None
        current = current.parent


def _parse_level(value: Any) -> int:
    try:
        return _LEVEL_NAMES[value.upper()]
    except (AttributeError, KeyError) as exc:
        raise _InvalidLoggingConfig(f"不明なログレベルです: {value!r}") from exc


def _parse_logging_table(table: dict[str, Any]) -> LoggingConfig:
    try:
        default_level = (
            _parse_level(table["level"]) if "level" in table else logging.INFO
        )
        file_path = Path(table["file"]) if "file" in table else None
        file_level = (
            _parse_level(table["file_level"]) if "file_level" in table else None
        )

        console_table = table.get("console", {})
        console_enabled = bool(console_table.get("enabled", True))
        console_level = (
            _parse_level(console_table["level"])
            if "level" in console_table
            else None
        )

        loggers = {
            name: _parse_logger_override(override_table)
            for name, override_table in table.get("loggers", {}).items()
        }
    except (AttributeError, TypeError) as exc:
        raise _InvalidLoggingConfig(str(exc)) from exc

    return LoggingConfig(
        default_level=default_level,
        console_enabled=console_enabled,
        console_level=console_level,
        file_path=file_path,
        file_level=file_level,
        loggers=loggers,
    )


def _parse_logger_override(override_table: dict[str, Any]) -> LoggerOverride:
    return LoggerOverride(
        file_path=Path(override_table["file"]) if "file" in override_table else None,
        level=_parse_level(override_table["level"]) if "level" in override_table else None,
        console_level=(
            _parse_level(override_table["console_level"])
            if "console_level" in override_table
            else None
        ),
    )
