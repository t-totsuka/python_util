"""`.pre-commit-config.yaml`のフックエントリが持つ成功時ステージング・失敗時ブロックの挙動を検証するテスト。"""

from __future__ import annotations

import subprocess
from pathlib import Path

PRE_COMMIT_CONFIG_PATH = Path(__file__).resolve().parents[2] / ".pre-commit-config.yaml"


def _load_pre_commit_entry() -> str:
    """`.pre-commit-config.yaml`のローカルフックentry文字列を読み取る。"""
    text = PRE_COMMIT_CONFIG_PATH.read_text(encoding="utf-8")
    entry_line = next(line for line in text.splitlines() if line.strip().startswith("entry:"))
    _, _, raw_value = entry_line.partition(":")
    return raw_value.strip()


def _init_git_repo_with_staged_evidence(tmp_path: Path) -> None:
    """一時ディレクトリにGitリポジトリを初期化しreports/test-evidence.mdを配置する。"""
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "test"], cwd=tmp_path, check=True, capture_output=True)
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    (reports_dir / "test-evidence.md").write_text("# evidence\n", encoding="utf-8")


def _staged_file_names(tmp_path: Path) -> str:
    """作業ディレクトリのステージング済みファイル一覧を取得する。"""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def test_結合_pre_commit_config_yamlのフックentryが_pdm_run_pytestを疑似成功コマンドに置換した場合_reports_test_evidence_mdをステージする(
    tmp_path: Path,
) -> None:
    entry = _load_pre_commit_entry().replace("pdm run pytest", "true")
    _init_git_repo_with_staged_evidence(tmp_path)

    result = subprocess.run(entry, shell=True, cwd=tmp_path, capture_output=True, text=True)

    assert result.returncode == 0
    assert "reports/test-evidence.md" in _staged_file_names(tmp_path)


def test_結合_pre_commit_config_yamlのフックentryが_pdm_run_pytestを疑似失敗コマンドに置換した場合_非0で終了しreports_test_evidence_mdをステージしない(
    tmp_path: Path,
) -> None:
    entry = _load_pre_commit_entry().replace("pdm run pytest", "false")
    _init_git_repo_with_staged_evidence(tmp_path)

    result = subprocess.run(entry, shell=True, cwd=tmp_path, capture_output=True, text=True)

    assert result.returncode != 0
    assert _staged_file_names(tmp_path) == ""
