"""progress_display の挙動設定を保持する値オブジェクト定義。"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ProgressDisplayConfig:
    """`progress_display` の挙動設定を保持するイミュータブルなデータクラス。"""

    auto_remove_finished: bool = False
    refresh_per_second: float = 10.0
