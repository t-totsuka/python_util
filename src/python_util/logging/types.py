"""ロギング設定の値オブジェクト定義。"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class LoggerOverride:
    """ロガー名単位の個別設定。"""

    file_path: Path | None = None
    level: int | None = None
    console_level: int | None = None


@dataclass(frozen=True)
class LoggingConfig:
    """`pyproject.toml` から解釈されたロギング設定全体。"""

    default_level: int = logging.INFO
    console_enabled: bool = True
    console_level: int | None = None
    file_path: Path | None = None
    file_level: int | None = None
    rotation_enabled: bool = True
    retention_days: int = 7
    loggers: dict[str, LoggerOverride] = field(default_factory=dict)
