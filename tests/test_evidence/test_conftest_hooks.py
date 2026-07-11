"""ルートconftest.pyのpytest_runtest_logreportフックの挙動を検証するテスト。"""

from __future__ import annotations

from datetime import datetime

import conftest as root_conftest
import pytest


def test_結合_pytest_runtest_logreportが_callが成功しteardownが失敗した場合_FAILEDとして記録する(
    pytester: pytest.Pytester,
) -> None:
    pytester.makepyfile(
        test_teardown_failure_sample="""
        import pytest

        @pytest.fixture
        def 壊れるフィクスチャ():
            yield
            raise RuntimeError("teardown failed")

        def test_サンプル(壊れるフィクスチャ):
            assert True
        """
    )

    pytester.runpytest_inprocess(plugins=[root_conftest])

    content = (pytester.path / "reports" / "test-evidence.md").read_text(encoding="utf-8")
    assert "| test_サンプル | 失敗 |" in content
    assert "teardown failed" in content


def test_結合_pytest_runtest_logreportが_全フェーズ成功した場合_PASSEDとして記録する(
    pytester: pytest.Pytester,
) -> None:
    pytester.makepyfile(
        test_passed_sample="""
        def test_サンプル成功():
            assert True
        """
    )

    pytester.runpytest_inprocess(plugins=[root_conftest])

    content = (pytester.path / "reports" / "test-evidence.md").read_text(encoding="utf-8")
    assert "| test_サンプル成功 | 成功 |" in content
    assert "## 失敗一覧" not in content


def test_結合_pytest_runtest_logreportが_スキップされた場合_SKIPPEDとして記録する(
    pytester: pytest.Pytester,
) -> None:
    pytester.makepyfile(
        test_skipped_sample="""
        import pytest

        @pytest.mark.skip(reason="skip test")
        def test_サンプルスキップ():
            assert True
        """
    )

    pytester.runpytest_inprocess(plugins=[root_conftest])

    content = (pytester.path / "reports" / "test-evidence.md").read_text(encoding="utf-8")
    assert "| test_サンプルスキップ | スキップ |" in content


def test_結合_pytest_runtest_logreportが_ネストしたpytesterセッション実行時_外側セッションの収集結果を汚染しない(
    pytester: pytest.Pytester,
) -> None:
    baseline = len(root_conftest.collected_results)
    pytester.makepyfile(
        test_isolation_sample="""
        def test_サンプル():
            assert True
        """
    )

    pytester.runpytest_inprocess(plugins=[root_conftest])

    assert len(root_conftest.collected_results) == baseline


def test_単体正常系_extract_subpackage_and_method_nameが_parametrizeされたnodeidを受け取った場合_接尾辞を保持したままmethod_nameを返す() -> (
    None
):
    subpackage, method_name = root_conftest._extract_subpackage_and_method_name(
        "tests/binary_string_codec/test_codec.py::test_x[param0]"
    )

    assert subpackage == "binary_string_codec"
    assert method_name == "test_x[param0]"


def test_結合_pytest_sessionstartが_セッション開始時_開始時刻をUTC日時として記録する(
    pytester: pytest.Pytester,
) -> None:
    pytester.makepyfile(
        test_sessionstart_sample="""
        def test_サンプル():
            assert True
        """
    )
    before = datetime.now()

    pytester.runpytest_inprocess(plugins=[root_conftest])

    after = datetime.now()
    content = (pytester.path / "reports" / "test-evidence.md").read_text(encoding="utf-8")
    started_at_line = next(line for line in content.splitlines() if line.startswith("- 実行開始:"))
    started_at = datetime.strptime(started_at_line.removeprefix("- 実行開始: "), "%Y-%m-%d %H:%M:%S")
    assert before.replace(microsecond=0) <= started_at <= after


def test_結合_pytest_sessionfinishが_セッション終了時_収集済みTestCaseResultからreports配下にMarkdownエビデンスを書き込む(
    pytester: pytest.Pytester,
) -> None:
    pytester.makepyfile(
        test_sessionfinish_sample="""
        def test_サンプル成功する():
            assert True
        """
    )

    pytester.runpytest_inprocess(plugins=[root_conftest])

    evidence_path = pytester.path / "reports" / "test-evidence.md"
    assert evidence_path.exists()
    content = evidence_path.read_text(encoding="utf-8")
    assert "test_サンプル成功する" in content


def test_結合_pytest_runtest_logreportが_parametrizeされたテストを実行した場合_パラメータ接尾辞を含むmethod_nameで記録する(
    pytester: pytest.Pytester,
) -> None:
    pytester.makepyfile(
        test_parametrize_sample="""
        import pytest

        @pytest.mark.parametrize("value", [1, 2])
        def test_サンプル(value):
            assert value in (1, 2)
        """
    )

    pytester.runpytest_inprocess(plugins=[root_conftest])

    content = (pytester.path / "reports" / "test-evidence.md").read_text(encoding="utf-8")
    assert "| test_サンプル[1] | 成功 |" in content
    assert "| test_サンプル[2] | 成功 |" in content


def test_結合_pytest_sessionfinishが_複数サブパッケージと失敗を含むスイート実行時_サブパッケージ別グルーピングと失敗一覧を含むMarkdownを生成する(
    pytester: pytest.Pytester,
) -> None:
    pytester.makepyfile(
        **{
            "tests/sample_pkg_a/test_ok": """
            def test_成功する():
                assert True
            """,
            "tests/sample_pkg_b/test_ng": """
            def test_失敗する():
                assert False
            """,
        }
    )

    pytester.runpytest_inprocess(plugins=[root_conftest])

    evidence_path = pytester.path / "reports" / "test-evidence.md"
    content = evidence_path.read_text(encoding="utf-8")
    assert "### sample_pkg_a" in content
    assert "### sample_pkg_b" in content
    assert "## 失敗一覧" in content
    assert "test_失敗する" in content
