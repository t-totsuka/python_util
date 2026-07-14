"""コンソール用・ファイル用ハンドラの構築。"""

from __future__ import annotations

import logging
import warnings
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

from rich.logging import RichHandler

_FILE_FORMAT = "%(asctime)s %(levelname)s %(name)s %(message)s"


def build_console_handler(level: int) -> logging.Handler:
    """Richベースのコンソール用ハンドラを構築する。"""
    handler = RichHandler()
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter("%(message)s"))
    return handler


def _rotation_namer(default_name: str) -> str:
    """標準ハンドラのデフォルト退避名 `{パス}.{日付}` を `{stem}-{日付}{拡張子}` へ変換する。"""
    base, _, date_suffix = default_name.rpartition(".")
    original = Path(base)
    return str(original.with_name(f"{original.stem}-{date_suffix}{original.suffix}"))


def build_file_handler(
    path: Path,
    level: int,
    *,
    rotation_enabled: bool = True,
    retention_days: int = 7,
) -> logging.Handler | None:
    """ファイル用ハンドラ（既定で日次ローテーション付き）を構築する。"""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        warnings.warn(f"ログ出力先ディレクトリの作成に失敗しました: {path.parent} ({exc})")
        return None

    handler: logging.FileHandler
    if rotation_enabled:
        handler = TimedRotatingFileHandler(
            path,
            when="midnight",
            backupCount=retention_days,
            encoding="utf-8",
        )
        handler.namer = _rotation_namer
    else:
        handler = logging.FileHandler(path, mode="a", encoding="utf-8")
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter(_FILE_FORMAT))
    return handler
