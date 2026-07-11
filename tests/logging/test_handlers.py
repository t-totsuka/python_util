"""Handler Builder (`build_console_handler` / `build_file_handler`) を検証するテスト。"""

import logging

import pytest
from rich.logging import RichHandler

from python_util.logging.handlers import build_console_handler, build_file_handler


def test_単体正常系_build_console_handlerが_ログレベルを受け取った場合_整形済みのRichHandlerを返す():
    handler = build_console_handler(logging.WARNING)

    assert isinstance(handler, RichHandler)
    assert handler.level == logging.WARNING
    assert handler.formatter is not None
    assert handler.formatter._fmt == "%(message)s"


def test_単体正常系_build_file_handlerが_出力先ディレクトリが存在しない場合_ディレクトリを作成する(tmp_path):
    target = tmp_path / "logs" / "nested" / "app.log"

    handler = build_file_handler(target, logging.INFO)

    assert target.parent.is_dir()
    assert isinstance(handler, logging.FileHandler)
    assert handler.level == logging.INFO
    handler.close()


def test_単体正常系_build_file_handlerが_ログ出力を受け取った場合_時刻レベル名メッセージ形式で追記する(tmp_path):
    target = tmp_path / "app.log"

    handler = build_file_handler(target, logging.DEBUG)
    logger = logging.getLogger("test_handlers.append")
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    logger.info("hello world")
    handler.close()
    logger.removeHandler(handler)

    content = target.read_text()
    assert "hello world" in content
    assert "INFO" in content
    assert "test_handlers.append" in content


def test_異常系_build_file_handlerが_ディレクトリ作成に失敗した場合_警告を出しNoneを返す(
    tmp_path,
):
    blocked = tmp_path / "blocked"
    blocked.write_text("this is a file, not a directory")
    target = blocked / "app.log"

    with pytest.warns(UserWarning):
        handler = build_file_handler(target, logging.INFO)

    assert handler is None


def test_単体正常系_コンソールハンドラとファイルハンドラが_異なるレベルで構築された場合_互いに独立したレベルを保持する(tmp_path):
    console_handler = build_console_handler(logging.ERROR)
    file_handler = build_file_handler(tmp_path / "app.log", logging.DEBUG)

    assert console_handler.level == logging.ERROR
    assert file_handler.level == logging.DEBUG
    file_handler.close()
