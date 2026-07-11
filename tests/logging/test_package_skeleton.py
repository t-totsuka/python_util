"""python_util.logging サブパッケージの雛形がインポート可能であることを確認するテスト。"""

import importlib


def test_logging_package_is_importable():
    module = importlib.import_module("python_util.logging")
    assert module is not None


def test_logging_submodules_are_importable():
    for submodule_name in ("types", "config_loader", "handlers", "factory"):
        module = importlib.import_module(f"python_util.logging.{submodule_name}")
        assert module is not None
