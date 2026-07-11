"""複数モジュール構成での統合シナリオを、実ファイルシステムを用いて検証する結合テスト。"""

import logging
import textwrap
from pathlib import Path

import pytest

import python_util.logging.factory as factory_module
from python_util.logging.factory import get_logger


def _write_pyproject(path: Path, content: str) -> None:
    (path / "pyproject.toml").write_text(textwrap.dedent(content))


@pytest.fixture(autouse=True)
def reset_factory_state():
    factory_module._reset_registry()
    yield
    factory_module._reset_registry()


def test_結合_複数モジュールが_同一ファイル設定を共有する場合_単一のログファイルへ集約される(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _write_pyproject(tmp_path, """
        [tool.python_util.logging]
        file = "app.log"
        """)

    logger_a = get_logger("moduleA")
    logger_b = get_logger("moduleB")
    logger_a.info("message from module A")
    logger_b.info("message from module B")
    for logger in (logger_a, logger_b):
        for handler in logger.handlers:
            handler.flush()

    content = (tmp_path / "app.log").read_text()
    assert "message from module A" in content
    assert "message from module B" in content


def test_結合_特定ロガーにファイルオーバーライドが設定された場合_出力ファイルが分離される(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _write_pyproject(tmp_path, """
        [tool.python_util.logging]
        file = "app.log"

        [tool.python_util.logging.loggers.moduleA]
        file = "module_a.log"
        """)

    logger_a = get_logger("moduleA")
    logger_b = get_logger("moduleB")
    logger_a.info("only in module a log")
    logger_b.info("only in app log")
    for logger in (logger_a, logger_b):
        for handler in logger.handlers:
            handler.flush()

    module_a_content = (tmp_path / "module_a.log").read_text()
    app_content = (tmp_path / "app.log").read_text()

    assert "only in module a log" in module_a_content
    assert "only in module a log" not in app_content
    assert "only in app log" in app_content
    assert "only in app log" not in module_a_content


def test_結合_ロガーが_コンソールとファイル両方に設定された場合_両方が同一メッセージを受け取る(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    _write_pyproject(tmp_path, """
        [tool.python_util.logging]
        file = "app.log"
        """)

    logger = get_logger("moduleC")
    logger.warning("dual output message")
    for handler in logger.handlers:
        handler.flush()

    file_content = (tmp_path / "app.log").read_text()
    console_output = capsys.readouterr().out

    assert "dual output message" in file_content
    assert "dual output message" in console_output


def test_結合_ログレベルが設定された場合_ファイル出力にもレベルフィルタが適用される(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _write_pyproject(tmp_path, """
        [tool.python_util.logging]
        file = "app.log"
        level = "WARNING"
        """)

    logger = get_logger("moduleD")
    logger.info("should be filtered out")
    logger.warning("should be recorded")
    for handler in logger.handlers:
        handler.flush()

    content = (tmp_path / "app.log").read_text()
    assert "should be filtered out" not in content
    assert "should be recorded" in content
