"""Logger Factory (`get_logger`) を検証するテスト。"""

import logging
import threading
import time

import pytest
from rich.logging import RichHandler

import python_util.logging.factory as factory_module
from python_util.logging.factory import get_logger
from python_util.logging.types import LoggingConfig


@pytest.fixture(autouse=True)
def reset_factory_state():
    factory_module._reset_registry()
    yield
    factory_module._reset_registry()


def test_単体正常系_get_loggerが_名前を省略された場合_呼び出し元モジュール名を使用する(monkeypatch):
    monkeypatch.setattr(factory_module, "load_config", lambda start_dir=None: LoggingConfig())

    logger = get_logger()

    assert logger.name == __name__


def test_単体正常系_get_loggerが_名前を指定された場合_指定された名前を使用する(monkeypatch):
    monkeypatch.setattr(factory_module, "load_config", lambda start_dir=None: LoggingConfig())

    logger = get_logger("myapp.sample")

    assert logger.name == "myapp.sample"


def test_単体正常系_get_loggerが_設定なしで呼び出された場合_デフォルトでコンソールハンドラを付与する(monkeypatch):
    monkeypatch.setattr(factory_module, "load_config", lambda start_dir=None: LoggingConfig())

    logger = get_logger("myapp.console_only")

    assert any(isinstance(h, RichHandler) for h in logger.handlers)
    assert logger.propagate is False


def test_単体正常系_get_loggerが_ファイル出力が設定された場合_ファイルハンドラを付与する(tmp_path, monkeypatch):
    log_file = tmp_path / "app.log"
    config = LoggingConfig(file_path=log_file)
    monkeypatch.setattr(factory_module, "load_config", lambda start_dir=None: config)

    logger = get_logger("myapp.with_file")
    logger.info("hello file output")
    for handler in logger.handlers:
        handler.flush()

    assert "hello file output" in log_file.read_text()


def test_単体正常系_get_loggerが_コンソールとファイル両方が設定された場合_両方へ同時に出力する(tmp_path, monkeypatch, capsys):
    log_file = tmp_path / "app.log"
    config = LoggingConfig(file_path=log_file)
    monkeypatch.setattr(factory_module, "load_config", lambda start_dir=None: config)

    logger = get_logger("myapp.both")
    logger.warning("dual output message")
    for handler in logger.handlers:
        handler.flush()

    assert "dual output message" in log_file.read_text()


def test_単体正常系_get_loggerが_複数回呼び出された場合_設定読み込みは一度だけ行う(monkeypatch):
    calls: list[int] = []

    def fake_load_config(start_dir=None):
        calls.append(1)
        return LoggingConfig()

    monkeypatch.setattr(factory_module, "load_config", fake_load_config)

    get_logger("myapp.one")
    get_logger("myapp.two")

    assert len(calls) == 1


def test_単体正常系_get_loggerが_パッケージ公開APIとして_エクスポートされている():
    from python_util.logging import get_logger as exported_get_logger

    assert exported_get_logger is get_logger


def test_単体正常系_get_loggerが_同じ名前で繰り返し呼び出された場合_ハンドラを重複させない(monkeypatch):
    monkeypatch.setattr(factory_module, "load_config", lambda start_dir=None: LoggingConfig())

    first = get_logger("myapp.repeated")
    handler_count_after_first = len(first.handlers)
    second = get_logger("myapp.repeated")

    assert second is first
    assert len(second.handlers) == handler_count_after_first


def test_境界_get_loggerが_同じ名前で並行アクセスされた場合_ハンドラを一度だけ登録する(monkeypatch):
    monkeypatch.setattr(factory_module, "load_config", lambda start_dir=None: LoggingConfig())

    original_build_console_handler = factory_module.build_console_handler

    def slow_build_console_handler(level):
        time.sleep(0.02)
        return original_build_console_handler(level)

    monkeypatch.setattr(factory_module, "build_console_handler", slow_build_console_handler)

    barrier = threading.Barrier(20)

    def call_get_logger():
        barrier.wait()
        get_logger("myapp.concurrent")

    threads = [threading.Thread(target=call_get_logger) for _ in range(20)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    logger = logging.getLogger("myapp.concurrent")
    assert len(logger.handlers) == 1


def test_単体正常系_get_loggerが_既存ロガーを再取得した場合_同一のハンドラ一覧を保持する(monkeypatch):
    monkeypatch.setattr(factory_module, "load_config", lambda start_dir=None: LoggingConfig())

    first = get_logger("myapp.reuse")
    handlers_first = list(first.handlers)
    second = get_logger("myapp.reuse")

    assert list(second.handlers) == handlers_first


@pytest.mark.parametrize(
    "configured_level,below_level",
    [
        (logging.INFO, logging.DEBUG),
        (logging.WARNING, logging.INFO),
        (logging.ERROR, logging.WARNING),
        (logging.CRITICAL, logging.ERROR),
    ],
)
def test_単体正常系_get_loggerが_設定レベル未満のメッセージを受け取った場合_出力から除外する(
    tmp_path, monkeypatch, configured_level, below_level
):
    log_file = tmp_path / "app.log"
    config = LoggingConfig(default_level=configured_level, file_path=log_file)
    monkeypatch.setattr(factory_module, "load_config", lambda start_dir=None: config)

    logger = get_logger(f"myapp.level.{configured_level}")
    logger.log(below_level, "below threshold message")
    logger.log(configured_level, "at threshold message")
    for handler in logger.handlers:
        handler.flush()

    content = log_file.read_text()
    assert "at threshold message" in content
    assert "below threshold message" not in content


def test_単体正常系_コンソールとファイルが_異なるレベルで設定された場合_それぞれ独立にフィルタする(tmp_path, monkeypatch, capsys):
    log_file = tmp_path / "app.log"
    config = LoggingConfig(
        file_path=log_file, console_level=logging.ERROR, file_level=logging.DEBUG
    )
    monkeypatch.setattr(factory_module, "load_config", lambda start_dir=None: config)

    logger = get_logger("myapp.independent_levels")
    logger.warning("warning level message")
    for handler in logger.handlers:
        handler.flush()

    file_content = log_file.read_text()
    console_output = capsys.readouterr().out

    assert "warning level message" in file_content
    assert "warning level message" not in console_output
