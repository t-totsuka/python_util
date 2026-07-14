"""設定不備・環境不備時のフォールバック経路を、実ファイルシステムを用いて検証する結合テスト。"""

import logging
import textwrap
from pathlib import Path

import pytest
from rich.logging import RichHandler

import python_util.logging.factory as factory_module
from python_util.logging.config_loader import load_config
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


@pytest.mark.parametrize(
    "invalid_rotation_toml, logger_name",
    [
        ("retention_days = 0", "moduleInvalidRotationZero"),
        ("retention_days = true", "moduleInvalidRotationBool"),
    ],
    ids=["retention_daysがゼロ", "retention_daysがbool値"],
)
def test_異常系_get_loggerが_不正なrotation設定を受け取った場合_警告を出しデフォルト設定にフォールバックする(
    tmp_path, monkeypatch, invalid_rotation_toml, logger_name
):
    # rotation関連の不正値は、既存パターン（要件3.5）と同一の「設定全体フォールバック」対象となるため、
    # 同一テーブル内に指定した`file`設定も含めデフォルトのLoggingConfig（ローテーション有効・保持7日を含む）
    # へフォールバックする（design.md Error Handling節、config_loader._parse_logging_tableの実装を参照）。
    # そのため、この不正rotation設定下ではファイルハンドラは構築されず、コンソール出力のみとなる。
    monkeypatch.chdir(tmp_path)
    _write_pyproject(tmp_path, f"""
        [tool.python_util.logging]
        file = "app.log"

        [tool.python_util.logging.rotation]
        {invalid_rotation_toml}
        """)

    with pytest.warns(UserWarning):
        logger = get_logger(logger_name)
    logger.info("should not raise")

    assert len(logger.handlers) == 1
    assert isinstance(logger.handlers[0], RichHandler)
    # 設定全体フォールバックにより`file`設定も破棄されるため、ログファイルは生成されない。
    assert not (tmp_path / "app.log").exists()

    # フォールバック後の`LoggingConfig`自体は既定のローテーション設定（有効・保持7日）であることを
    # 直接確認する（要件6.1, 6.6, 7.3）。ファイル設定を伴わないため、実際のハンドラのbackupCount等では
    # 観測できないための補完確認。
    fallback_config = load_config(start_dir=tmp_path)
    assert fallback_config.rotation_enabled is True
    assert fallback_config.retention_days == 7


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
