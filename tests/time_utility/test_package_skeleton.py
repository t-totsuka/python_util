"""python_util.time_utility サブパッケージの雛形がインポート可能であることを確認するテスト。"""

import importlib


def test_time_utility_package_is_importable():
    module = importlib.import_module("python_util.time_utility")
    assert module is not None
