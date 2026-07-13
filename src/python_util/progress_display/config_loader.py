"""呼び出し側 pyproject.toml の探索・解析。"""

from __future__ import annotations

import threading
import warnings
from pathlib import Path
from typing import Any

from python_util._pyproject import load_tool_table
from python_util.progress_display.exceptions import _InvalidProgressDisplayConfig
from python_util.progress_display.types import ProgressDisplayConfig

_config_cache: ProgressDisplayConfig | None = None
_config_cache_lock = threading.Lock()


def load_config(start_dir: Path | None = None) -> ProgressDisplayConfig:
    """呼び出し側 pyproject.toml の設定テーブルを読み込み、失敗時はデフォルトにフォールバックする。"""
    table, pyproject_path = load_tool_table(start_dir, "progress_display")
    if table is None:
        return ProgressDisplayConfig()

    try:
        return _parse_progress_display_table(table)
    except _InvalidProgressDisplayConfig as exc:
        warnings.warn(f"{pyproject_path} の [tool.python_util.progress_display] が不正です: {exc}")
        return ProgressDisplayConfig()


def get_cached_config() -> ProgressDisplayConfig:
    """load_config() の結果をプロセス内でキャッシュして返す。"""
    global _config_cache
    with _config_cache_lock:
        if _config_cache is None:
            _config_cache = load_config()
        return _config_cache


def _reset_config_cache() -> None:
    """テスト用: 設定キャッシュをリセットする。"""
    global _config_cache
    with _config_cache_lock:
        _config_cache = None


def _parse_progress_display_table(table: dict[str, Any]) -> ProgressDisplayConfig:
    auto_remove_finished = table.get("auto_remove_finished", False)
    if not isinstance(auto_remove_finished, bool):
        raise _InvalidProgressDisplayConfig(
            f"auto_remove_finished は bool である必要があります: {auto_remove_finished!r}"
        )

    refresh_per_second_raw = table.get("refresh_per_second", 10.0)
    try:
        refresh_per_second = float(refresh_per_second_raw)
    except (TypeError, ValueError) as exc:
        raise _InvalidProgressDisplayConfig(
            f"refresh_per_second は数値である必要があります: {refresh_per_second_raw!r}"
        ) from exc

    if refresh_per_second <= 0:
        raise _InvalidProgressDisplayConfig(
            f"refresh_per_second は正の値である必要があります: {refresh_per_second!r}"
        )

    return ProgressDisplayConfig(
        auto_remove_finished=auto_remove_finished,
        refresh_per_second=refresh_per_second,
    )
