"""Handler Builder (`build_console_handler` / `build_file_handler`) を検証するテスト。"""

from __future__ import annotations

import datetime
import logging
from logging.handlers import TimedRotatingFileHandler

import pytest
from rich.logging import RichHandler

from python_util.logging.handlers import build_console_handler, build_file_handler


def _make_record(message: str) -> logging.LogRecord:
    """テスト用のLogRecordを生成する。"""
    return logging.LogRecord(
        name="test_handlers.rotation",
        level=logging.INFO,
        pathname=__file__,
        lineno=0,
        msg=message,
        args=(),
        exc_info=None,
    )


def _midnight_today_epoch() -> int:
    """ローカル時刻の当日深夜0時のepoch秒を返す。"""
    midnight = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
    return int(midnight.timestamp())


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


def test_単体正常系_build_file_handlerが_非ASCII文字を出力した場合_ロケールに依存せずUTF8で書き込む(tmp_path):
    target = tmp_path / "app.log"

    handler = build_file_handler(target, logging.DEBUG)
    logger = logging.getLogger("test_handlers.utf8")
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    logger.info("日本語と絵文字🚀を含むメッセージ")
    handler.close()
    logger.removeHandler(handler)

    assert handler.encoding == "utf-8"
    content = target.read_text(encoding="utf-8")
    assert "日本語と絵文字🚀を含むメッセージ" in content


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


def test_単体正常系_build_file_handlerが_ローテーション有効の場合_日次ローテーションのハンドラを構築する(tmp_path):
    target = tmp_path / "app.log"

    handler = build_file_handler(target, logging.INFO, rotation_enabled=True, retention_days=5)

    assert isinstance(handler, TimedRotatingFileHandler)
    assert handler.when == "MIDNIGHT"
    assert handler.backupCount == 5
    assert handler.encoding == "utf-8"
    assert handler.utc is False
    assert handler.level == logging.INFO
    assert handler.formatter is not None
    assert handler.formatter._fmt == "%(asctime)s %(levelname)s %(name)s %(message)s"
    handler.close()


def test_単体正常系_build_file_handlerが_ローテーション無効の場合_追記モードの単一ファイルハンドラを構築する(tmp_path):
    target = tmp_path / "app.log"

    handler = build_file_handler(target, logging.INFO, rotation_enabled=False)

    assert isinstance(handler, logging.FileHandler)
    assert not isinstance(handler, TimedRotatingFileHandler)
    assert handler.mode == "a"
    assert handler.encoding == "utf-8"
    handler.close()


def test_単体正常系_namerが_デフォルト退避名を受け取った場合_stemハイフン日付拡張子の形式へ変換する(tmp_path):
    target = tmp_path / "app.log"

    handler = build_file_handler(target, logging.INFO)

    assert handler.namer is not None
    converted = handler.namer(f"{target}.2026-07-13")
    assert converted == str(tmp_path / "app-2026-07-13.log")
    handler.close()


def test_単体正常系_namerが_日付形式の文字列を含むファイル名を受け取った場合_末尾サフィックスのみを日付として扱う(tmp_path):
    target = tmp_path / "run-2026-07-01.log"

    handler = build_file_handler(target, logging.INFO)

    converted = handler.namer(f"{target}.2026-07-13")
    assert converted == str(tmp_path / "run-2026-07-01-2026-07-13.log")
    handler.close()


def test_結合正常系_ローテーション有効のハンドラが_日付境界を越えて書き込んだ場合_当日ファイルを日付付き退避ファイルへ移す(tmp_path):
    target = tmp_path / "app.log"
    today = datetime.date.today()
    handler = build_file_handler(target, logging.INFO)

    handler.emit(_make_record("before rollover"))
    handler.rolloverAt = _midnight_today_epoch()
    handler.emit(_make_record("after rollover"))
    handler.close()

    yesterday = (today - datetime.timedelta(days=1)).isoformat()
    archived = tmp_path / f"app-{yesterday}.log"
    assert archived.is_file()
    assert "before rollover" in archived.read_text(encoding="utf-8")
    assert "after rollover" in target.read_text(encoding="utf-8")
    assert "before rollover" not in target.read_text(encoding="utf-8")


def test_結合正常系_ローテーション有効のハンドラが_保持世代数を超えた場合_古い退避ファイルから削除する(tmp_path):
    target = tmp_path / "app.log"
    today = datetime.date.today()
    old_dates = ["2026-01-01", "2026-01-02", "2026-01-03", "2026-01-04"]
    for old_date in old_dates:
        (tmp_path / f"app-{old_date}.log").write_text(f"archived {old_date}\n", encoding="utf-8")
    handler = build_file_handler(target, logging.INFO, retention_days=3)

    handler.emit(_make_record("before rollover"))
    handler.rolloverAt = _midnight_today_epoch()
    handler.emit(_make_record("after rollover"))
    handler.close()

    yesterday = (today - datetime.timedelta(days=1)).isoformat()
    assert not (tmp_path / "app-2026-01-01.log").exists()
    assert not (tmp_path / "app-2026-01-02.log").exists()
    assert (tmp_path / "app-2026-01-03.log").is_file()
    assert (tmp_path / "app-2026-01-04.log").is_file()
    assert (tmp_path / f"app-{yesterday}.log").is_file()
