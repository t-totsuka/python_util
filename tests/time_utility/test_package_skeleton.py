"""python_util.time_utility サブパッケージの雛形がインポート可能であることを確認するテスト。"""

import importlib


def test_単体正常系_time_utilityパッケージが_インポートされた場合_モジュールとして取得できる():
    module = importlib.import_module("python_util.time_utility")
    assert module is not None
