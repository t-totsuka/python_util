"""Config Loader (`load_config` / `resolve_logger_override`) を検証するテスト。"""

import logging
import textwrap
from pathlib import Path

import pytest

from python_util.logging.config_loader import load_config, resolve_logger_override
from python_util.logging.types import LoggerOverride, LoggingConfig


def _write(path: Path, content: str) -> None:
    path.write_text(textwrap.dedent(content))


def test_単体正常系_load_configが_pyproject_tomlが見つからない場合_デフォルト設定を返す(tmp_path):
    start_dir = tmp_path / "no_pyproject"
    start_dir.mkdir()

    config = load_config(start_dir=start_dir)

    assert config == LoggingConfig()


def test_単体正常系_load_configが_toolテーブルが存在しない場合_デフォルト設定を返す(tmp_path):
    _write(tmp_path / "pyproject.toml", """
        [project]
        name = "sample"
        """)

    config = load_config(start_dir=tmp_path)

    assert config == LoggingConfig()


def test_単体正常系_load_configが_完全な設定テーブルを受け取った場合_全項目を解析する(tmp_path):
    _write(tmp_path / "pyproject.toml", """
        [tool.python_util.logging]
        level = "DEBUG"
        file = "logs/app.log"
        file_level = "WARNING"

        [tool.python_util.logging.console]
        enabled = false
        level = "ERROR"

        [tool.python_util.logging.loggers."myapp.worker"]
        file = "logs/worker.log"
        level = "INFO"
        """)

    config = load_config(start_dir=tmp_path)

    assert config.default_level == logging.DEBUG
    assert config.file_path == Path("logs/app.log")
    assert config.file_level == logging.WARNING
    assert config.console_enabled is False
    assert config.console_level == logging.ERROR
    assert config.loggers == {
        "myapp.worker": LoggerOverride(
            file_path=Path("logs/worker.log"), level=logging.INFO
        )
    }


def test_異常系_load_configが_TOML構文エラーを含む場合_警告を出しデフォルト設定にフォールバックする(tmp_path):
    _write(tmp_path / "pyproject.toml", "this is not valid toml [[[")

    with pytest.warns(UserWarning):
        config = load_config(start_dir=tmp_path)

    assert config == LoggingConfig()


def test_異常系_load_configが_未知のログレベル文字列を受け取った場合_警告を出しデフォルト設定にフォールバックする(tmp_path):
    _write(tmp_path / "pyproject.toml", """
        [tool.python_util.logging]
        level = "NOT_A_LEVEL"
        """)

    with pytest.warns(UserWarning):
        config = load_config(start_dir=tmp_path)

    assert config == LoggingConfig()


def test_単体正常系_load_configが_子ディレクトリから開始した場合_親ディレクトリのpyproject_tomlを探索する(tmp_path):
    _write(tmp_path / "pyproject.toml", """
        [tool.python_util.logging]
        level = "ERROR"
        """)
    child_dir = tmp_path / "src" / "app"
    child_dir.mkdir(parents=True)

    config = load_config(start_dir=child_dir)

    assert config.default_level == logging.ERROR


def test_境界_load_configが_複数階層にpyproject_tomlが存在する場合_最初に見つかったもののみを考慮する(tmp_path):
    _write(tmp_path / "pyproject.toml", """
        [tool.python_util.logging]
        level = "ERROR"
        """)
    child_dir = tmp_path / "child"
    child_dir.mkdir()
    _write(child_dir / "pyproject.toml", """
        [project]
        name = "child"
        """)

    config = load_config(start_dir=child_dir)

    assert config == LoggingConfig()


def test_単体正常系_resolve_logger_overrideが_複数のプレフィックスに一致する場合_最長一致のオーバーライドを返す():
    config = LoggingConfig(
        loggers={
            "myapp": LoggerOverride(level=logging.WARNING),
            "myapp.worker": LoggerOverride(level=logging.DEBUG),
        }
    )

    override = resolve_logger_override(config, "myapp.worker.io")

    assert override == LoggerOverride(level=logging.DEBUG)


def test_単体正常系_resolve_logger_overrideが_一致するロガー名がない場合_Noneを返す():
    config = LoggingConfig(loggers={"myapp": LoggerOverride(level=logging.WARNING)})

    override = resolve_logger_override(config, "otherapp.io")

    assert override is None
