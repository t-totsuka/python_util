"""ProgressDisplayConfig の仕様を検証するテスト。"""

import dataclasses

import pytest

from python_util.progress_display.types import ProgressDisplayConfig


def test_default_instance_has_expected_defaults():
    config = ProgressDisplayConfig()

    assert config.auto_remove_finished is False
    assert config.refresh_per_second == 10.0


def test_instance_is_frozen():
    config = ProgressDisplayConfig()

    with pytest.raises(dataclasses.FrozenInstanceError):
        config.auto_remove_finished = True


def test_can_override_values_at_construction():
    config = ProgressDisplayConfig(auto_remove_finished=True, refresh_per_second=5.0)

    assert config.auto_remove_finished is True
    assert config.refresh_per_second == 5.0
