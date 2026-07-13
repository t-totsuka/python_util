"""呼び出し側 pyproject.toml の探索・解析。"""

from __future__ import annotations

import tomllib
import warnings
from pathlib import Path
from typing import Any

from python_util.progress_display.exceptions import _InvalidProgressDisplayConfig
from python_util.progress_display.types import ProgressDisplayConfig


def load_config(start_dir: Path | None = None) -> ProgressDisplayConfig:
    """呼び出し側 pyproject.toml の設定テーブルを読み込み、失敗時はデフォルトにフォールバックする。"""
    base_dir = start_dir if start_dir is not None else Path.cwd()
    pyproject_path = _find_pyproject_toml(base_dir)
    if pyproject_path is None:
        return ProgressDisplayConfig()

    try:
        data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    except (tomllib.TOMLDecodeError, UnicodeDecodeError) as exc:
        warnings.warn(f"{pyproject_path} の解析に失敗しました: {exc}")
        return ProgressDisplayConfig()

    table = data.get("tool", {}).get("python_util", {}).get("progress_display")
    if table is None:
        return ProgressDisplayConfig()

    try:
        return _parse_progress_display_table(table)
    except _InvalidProgressDisplayConfig as exc:
        warnings.warn(f"{pyproject_path} の [tool.python_util.progress_display] が不正です: {exc}")
        return ProgressDisplayConfig()


def _find_pyproject_toml(start_dir: Path) -> Path | None:
    current = start_dir
    while True:
        candidate = current / "pyproject.toml"
        if candidate.is_file():
            return candidate
        if current.parent == current:
            return None
        current = current.parent


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
