"""複数モジュール構成での統合シナリオを、実ファイルシステムを用いて検証する結合テスト。"""

import datetime
import logging
import textwrap
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

import pytest

import python_util.logging.factory as factory_module
from python_util.logging.factory import get_logger


def _write_pyproject(path: Path, content: str) -> None:
    (path / "pyproject.toml").write_text(textwrap.dedent(content))


def _midnight_today_epoch() -> int:
    """ローカル時刻の当日深夜0時のepoch秒を返す。"""
    midnight = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
    return int(midnight.timestamp())


def _rotating_file_handler(logger: logging.Logger) -> TimedRotatingFileHandler:
    """ロガーが保持する`TimedRotatingFileHandler`を取得する。"""
    for handler in logger.handlers:
        if isinstance(handler, TimedRotatingFileHandler):
            return handler
    raise AssertionError(f"TimedRotatingFileHandlerが見つかりません: {logger.handlers}")


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


def test_結合_日付変更を模擬した場合_当日ファイルが退避ファイルへ移り新しい当日ファイルへ書き込みが継続される(
    tmp_path, monkeypatch
):
    monkeypatch.chdir(tmp_path)
    _write_pyproject(tmp_path, """
        [tool.python_util.logging]
        file = "app.log"
        """)
    today = datetime.date.today()

    logger = get_logger("moduleRotationSingle")
    handler = _rotating_file_handler(logger)

    logger.info("before rollover")
    handler.flush()
    handler.rolloverAt = _midnight_today_epoch()
    logger.info("after rollover")
    handler.flush()

    yesterday = (today - datetime.timedelta(days=1)).isoformat()
    archived = tmp_path / f"app-{yesterday}.log"
    current = tmp_path / "app.log"

    assert archived.is_file()
    assert "before rollover" in archived.read_text(encoding="utf-8")
    assert "after rollover" in current.read_text(encoding="utf-8")
    assert "before rollover" not in current.read_text(encoding="utf-8")


def test_結合_保持世代数を超える退避ファイルが事前配置されている場合_古いものから削除される(
    tmp_path, monkeypatch
):
    monkeypatch.chdir(tmp_path)
    _write_pyproject(tmp_path, """
        [tool.python_util.logging]
        file = "app.log"

        [tool.python_util.logging.rotation]
        retention_days = 3
        """)
    today = datetime.date.today()
    old_dates = ["2026-01-01", "2026-01-02", "2026-01-03", "2026-01-04"]
    for old_date in old_dates:
        (tmp_path / f"app-{old_date}.log").write_text(
            f"archived {old_date}\n", encoding="utf-8"
        )

    logger = get_logger("moduleRotationRetention")
    handler = _rotating_file_handler(logger)

    logger.info("before rollover")
    handler.flush()
    handler.rolloverAt = _midnight_today_epoch()
    logger.info("after rollover")
    handler.flush()

    yesterday = (today - datetime.timedelta(days=1)).isoformat()
    assert not (tmp_path / "app-2026-01-01.log").exists()
    assert not (tmp_path / "app-2026-01-02.log").exists()
    assert (tmp_path / "app-2026-01-03.log").is_file()
    assert (tmp_path / "app-2026-01-04.log").is_file()
    assert (tmp_path / f"app-{yesterday}.log").is_file()


def test_結合_複数モジュールが単一ファイルへ統合された構成で_日付変更後も新しい当日ファイルにのみ記録される(
    tmp_path, monkeypatch
):
    monkeypatch.chdir(tmp_path)
    _write_pyproject(tmp_path, """
        [tool.python_util.logging]
        file = "app.log"
        """)
    today = datetime.date.today()

    logger_a = get_logger("moduleRotationA")
    logger_b = get_logger("moduleRotationB")
    handler_a = _rotating_file_handler(logger_a)
    handler_b = _rotating_file_handler(logger_b)
    assert handler_a is handler_b  # 同一パスのためハンドラは共有される（タスク6.2）

    logger_a.info("A message before rollover")
    logger_b.info("B message before rollover")
    handler_a.flush()
    handler_a.rolloverAt = _midnight_today_epoch()
    logger_a.info("A message after rollover")
    logger_b.info("B message after rollover")
    handler_a.flush()

    yesterday = (today - datetime.timedelta(days=1)).isoformat()
    archived_content = (tmp_path / f"app-{yesterday}.log").read_text(encoding="utf-8")
    current_content = (tmp_path / "app.log").read_text(encoding="utf-8")

    assert "A message before rollover" in archived_content
    assert "B message before rollover" in archived_content
    assert "A message after rollover" in current_content
    assert "B message after rollover" in current_content
    assert "A message after rollover" not in archived_content
    assert "B message after rollover" not in archived_content
    assert "A message before rollover" not in current_content
    assert "B message before rollover" not in current_content


def test_結合_rotation_enabledがfalseの場合_ローテーションが発生せず単一ファイルへ追記され続ける(
    tmp_path, monkeypatch
):
    monkeypatch.chdir(tmp_path)
    _write_pyproject(tmp_path, """
        [tool.python_util.logging]
        file = "app.log"

        [tool.python_util.logging.rotation]
        enabled = false
        """)

    logger = get_logger("moduleRotationDisabled")
    file_handlers = [
        handler for handler in logger.handlers if isinstance(handler, logging.FileHandler)
    ]
    assert len(file_handlers) == 1
    handler = file_handlers[0]
    assert not isinstance(handler, TimedRotatingFileHandler)

    logger.info("first message")
    handler.flush()
    # 日付変更相当の状況を作ってもrotation.enabled=falseではTimedRotatingFileHandlerではないため
    # rolloverAt自体が存在せず、ローテーションの契機がないことを確認する。
    assert not hasattr(handler, "rolloverAt")
    logger.info("second message")
    handler.flush()

    current = tmp_path / "app.log"
    content = current.read_text(encoding="utf-8")
    assert "first message" in content
    assert "second message" in content
    assert list(tmp_path.glob("app-*.log")) == []


def test_結合_retention_daysが設定された場合_ファイルハンドラのbackupCountへ反映される(
    tmp_path, monkeypatch
):
    monkeypatch.chdir(tmp_path)
    _write_pyproject(tmp_path, """
        [tool.python_util.logging]
        file = "app.log"

        [tool.python_util.logging.rotation]
        retention_days = 3
        """)

    logger = get_logger("moduleRetentionDaysReflected")
    handler = _rotating_file_handler(logger)

    assert handler.backupCount == 3


def test_結合_ロガー個別ファイル設定でも同一のローテーション動作が適用される(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _write_pyproject(tmp_path, """
        [tool.python_util.logging]
        file = "app.log"

        [tool.python_util.logging.loggers.moduleRotationIndividual]
        file = "module_a.log"
        """)
    today = datetime.date.today()

    logger = get_logger("moduleRotationIndividual")
    handler = _rotating_file_handler(logger)

    logger.info("before rollover")
    handler.flush()
    handler.rolloverAt = _midnight_today_epoch()
    logger.info("after rollover")
    handler.flush()

    yesterday = (today - datetime.timedelta(days=1)).isoformat()
    archived = tmp_path / f"module_a-{yesterday}.log"
    current = tmp_path / "module_a.log"

    assert archived.is_file()
    assert "before rollover" in archived.read_text(encoding="utf-8")
    assert "after rollover" in current.read_text(encoding="utf-8")
    assert "before rollover" not in current.read_text(encoding="utf-8")
