"""呼び出し側 pyproject.toml の探索と [tool.python_util.*] テーブルの読み込み。"""

from __future__ import annotations

import tomllib
import warnings
from pathlib import Path
from typing import Any


def find_pyproject_toml(start_dir: Path) -> Path | None:
    current = start_dir
    while True:
        candidate = current / "pyproject.toml"
        if candidate.is_file():
            return candidate
        if current.parent == current:
            return None
        current = current.parent


def load_tool_table(
    start_dir: Path | None, table_name: str
) -> tuple[Any | None, Path | None]:
    """[tool.python_util.<table_name>] テーブルと pyproject.toml のパスを返す。

    pyproject.toml が見つからない・読み取れない・テーブルが存在しない場合は
    テーブルとして None を返す(読み取り失敗時は警告を発する)。
    """
    base_dir = start_dir if start_dir is not None else Path.cwd()
    pyproject_path = find_pyproject_toml(base_dir)
    if pyproject_path is None:
        return None, None

    try:
        data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    except (tomllib.TOMLDecodeError, UnicodeDecodeError) as exc:
        warnings.warn(f"{pyproject_path} の解析に失敗しました: {exc}")
        return None, pyproject_path

    return data.get("tool", {}).get("python_util", {}).get(table_name), pyproject_path
