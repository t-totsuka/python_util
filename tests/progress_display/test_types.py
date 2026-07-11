"""ProgressDisplayConfig の仕様を検証するテスト。"""

import dataclasses

import pytest

from python_util.progress_display.types import ProgressDisplayConfig


def test_単体正常系_ProgressDisplayConfigが_デフォルト値で生成された場合_期待されるデフォルト値を持つ():
    config = ProgressDisplayConfig()

    assert config.auto_remove_finished is False
    assert config.refresh_per_second == 10.0


def test_単体正常系_ProgressDisplayConfigが_生成された場合_フィールド変更不可なイミュータブルである():
    config = ProgressDisplayConfig()

    with pytest.raises(dataclasses.FrozenInstanceError):
        config.auto_remove_finished = True


def test_単体正常系_ProgressDisplayConfigが_生成時に値を指定された場合_指定した値で上書きする():
    config = ProgressDisplayConfig(auto_remove_finished=True, refresh_per_second=5.0)

    assert config.auto_remove_finished is True
    assert config.refresh_per_second == 5.0
