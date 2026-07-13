"""progress_display テスト共通フィクスチャ。"""

import pytest

import python_util.progress_display.config_loader as config_loader_module


@pytest.fixture(autouse=True)
def reset_config_cache():
    config_loader_module._reset_config_cache()
    yield
    config_loader_module._reset_config_cache()
