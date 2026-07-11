"""設定不備・環境不備時のフォールバック経路を、実ファイルシステムを用いて検証する結合テスト。"""

import logging
import textwrap
from pathlib import Path

import pytest
from rich.logging import RichHandler

import python_util.logging.factory as factory_module
from python_util.logging.factory import get_logger


def _write_pyproject(path: Path, content: str) -> None:
    (path / "pyproject.toml").write_text(textwrap.dedent(content))


@pytest.fixture(autouse=True)
def reset_factory_state():
    factory_module._reset_registry()
    yield
    factory_module._reset_registry()


def test_結合_get_loggerが_pyproject_tomlが存在しない場合_コンソール出力のみにフォールバックする(
    tmp_path, monkeypatch
):
    monkeypatch.chdir(tmp_path)

    logger = get_logger("moduleE")
    logger.info("should not raise")

    assert len(logger.handlers) == 1
    assert isinstance(logger.handlers[0], RichHandler)


def test_異常系_get_loggerが_TOML構文エラーが存在する場合_警告を出しデフォルト設定にフォールバックする(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "pyproject.toml").write_text("this is not valid toml [[[")

    with pytest.warns(UserWarning):
        logger = get_logger("moduleF")
    logger.info("should not raise")

    assert len(logger.handlers) == 1
    assert isinstance(logger.handlers[0], RichHandler)


def test_異常系_get_loggerが_未知のログレベル文字列が設定された場合_警告を出しデフォルトレベルにフォールバックする(
    tmp_path, monkeypatch
):
    monkeypatch.chdir(tmp_path)
    _write_pyproject(tmp_path, """
        [tool.python_util.logging]
        level = "NOT_A_LEVEL"
        """)

    with pytest.warns(UserWarning):
        logger = get_logger("moduleG")
    logger.info("should not raise")

    assert logger.handlers[0].level == logging.INFO


def test_異常系_get_loggerが_ログディレクトリ作成に失敗した場合_警告を出しコンソール出力のみを継続する(
    tmp_path, monkeypatch
):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "blocked").write_text("this is a file, not a directory")
    _write_pyproject(tmp_path, """
        [tool.python_util.logging]
        file = "blocked/app.log"
        """)

    with pytest.warns(UserWarning):
        logger = get_logger("moduleH")
    logger.info("should not raise despite directory creation failure")

    assert len(logger.handlers) == 1
    assert isinstance(logger.handlers[0], RichHandler)
