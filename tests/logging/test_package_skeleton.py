"""python_util.logging サブパッケージの雛形がインポート可能であることを確認するテスト。"""

import importlib


def test_単体正常系_python_util_loggingパッケージが_インポートされた場合_モジュールを取得できる():
    module = importlib.import_module("python_util.logging")
    assert module is not None


def test_単体正常系_loggingサブモジュール群が_インポートされた場合_いずれも取得できる():
    for submodule_name in ("types", "config_loader", "handlers", "factory"):
        module = importlib.import_module(f"python_util.logging.{submodule_name}")
        assert module is not None
