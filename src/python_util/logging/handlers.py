"""コンソール用・ファイル用ハンドラの構築。"""

from __future__ import annotations

import logging
import warnings
from pathlib import Path

from rich.logging import RichHandler

_FILE_FORMAT = "%(asctime)s %(levelname)s %(name)s %(message)s"


def build_console_handler(level: int) -> logging.Handler:
    handler = RichHandler()
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter("%(message)s"))
    return handler


def build_file_handler(path: Path, level: int) -> logging.Handler | None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        warnings.warn(f"ログ出力先ディレクトリの作成に失敗しました: {path.parent} ({exc})")
        return None

    handler = logging.FileHandler(path, mode="a", encoding="utf-8")
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter(_FILE_FORMAT))
    return handler
