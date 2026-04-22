import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / ".opencode" / "scripts"))

from session_context_triggers import (
    build_main_branch_warning,
    build_merge_conflict_warning,
    build_orphaned_worktrees_warning,
    build_pair_mode_resume,
    build_protected_branch_warning,
    build_stale_stash_warning,
    build_uncommitted_work_warning,
    build_unpushed_commits_warning,
    get_diff_summary,
    get_stash_analysis,
    is_on_main_branch,
    is_on_protected_branch,
    is_pair_mode_branch,
    run_git,
)
from session_context_triggers import (
    main as triggers_main,
)


class TestRunGit:
    def test_returns_stripped_stdout_on_success(self):
        with patch.object(subprocess, "run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="  hello  \n")
            assert run_git(["status"]) == "hello"

    def test_returns_none_on_nonzero_exit(self):
        with patch.object(subprocess, "run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="error")
            assert run_git(["status"]) is None


class TestIsOnMainBranch:
    def test_on_main(self):
        with patch.object(subprocess, "run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="main\n")
            assert is_on_main_branch() is True

    def test_on_dev(self):
        with patch.object(subprocess, "run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="dev\n")
            assert is_on_main_branch() is False

    def test_on_feature_branch(self):
        with patch.object(subprocess, "run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="feature/123-xyz\n")
            assert is_on_main_branch() is False


class TestIsOnProtectedBranch:
    def test_on_main(self):
        with patch.object(subprocess, "run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="main\n")
            assert is_on_protected_branch() is True

    def test_on_dev(self):
        with patch.object(subprocess, "run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="dev\n")
            assert is_on_protected_branch() is True

    def test_on_feature_branch(self):
        with patch.object(subprocess, "run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="feature/123\n")
            assert is_on_protected_branch() is False


class TestIsPairModeBranch:
    def test_pair_feature(self):
        with patch.object(subprocess, "run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="pair-feature/123-xyz\n")
            is_pair, branch = is_pair_mode_branch()
            assert is_pair is True
            assert branch == "pair-feature/123-xyz"

    def test_pair_spec(self):
        with patch.object(subprocess, "run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="pair-spec/456-abc\n")
            is_pair, branch = is_pair_mode_branch()
            assert is_pair is True

    def test_regular_feature(self):
        with patch.object(subprocess, "run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="feature/789-xyz\n")
            is_pair, branch = is_pair_mode_branch()
            assert is_pair is False


class TestBuildMainBranchWarning:
    def test_warning_with_changes(self):
        result = build_main_branch_warning(True, ["M file1.py", "A file2.py"])
        assert "Production Branch" in result
        assert "2 uncommitted changes" in result

    def test_warning_without_changes(self):
        result = build_main_branch_warning(False, [])
        assert "Production Branch" in result
        assert "switch to `dev`" in result


class TestBuildPairModeResume:
    def test_resume_with_issue_number(self):
        with patch.object(subprocess, "run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="3 files changed\n1 insertions\n")
            result = build_pair_mode_resume("pair-feature/123-xyz")
            assert "Pair Mode Resumed" in result
            assert "#123" in result


class TestBuildUncommittedWorkWarning:
    def test_warning_output(self):
        result = build_uncommitted_work_warning(["file1.py", "file2.py"])
        assert "2 uncommitted change(s)" in result


class TestGetDiffSummary:
    def test_returns_structured_data_when_changes_exist(self):
        diff_stat_output = (
            " .opencode/scripts/session_context_triggers.py |  5 +++--\n"
            " .opencode/guidelines/117-session-trigger-behavior.md | 42 +++++++++++++++++++\n"
            " 2 files changed, 37 insertions(+), 10 deletions(-)"
        )
        with patch("session_context_triggers.run_git", return_value=diff_stat_output):
            result = get_diff_summary()
        assert result is not None
        assert result["file_count"] == 2
        assert result["insertions"] == 37
        assert result["deletions"] == 10
        assert len(result["key_files"]) == 2

    def test_returns_none_when_no_changes(self):
        with patch("session_context_triggers.run_git", return_value=None):
            result = get_diff_summary()
        assert result is None

    def test_excludes_lockfiles_from_key_files(self):
        diff_stat_output = (
            " package-lock.json | 500 ++++++\n"
            " src/main.py         |  10 +- \n"
            " 2 files changed, 500 insertions(+), 5 deletions(-)"
        )
        with patch("session_context_triggers.run_git", return_value=diff_stat_output):
            result = get_diff_summary()
        assert result is not None
        assert "package-lock.json" not in result["key_files"]
        assert "src/main.py" in result["key_files"]

    def test_limits_key_files_to_five(self):
        lines = [f" src/file{i}.py |  5 +- \n" for i in range(10)]
        diff_stat_output = "\n".join(lines) + "\n 10 files changed, 50 insertions(+), 50 deletions(-)"
        with patch("session_context_triggers.run_git", return_value=diff_stat_output):
            result = get_diff_summary()
        assert result is not None
        assert len(result["key_files"]) <= 5


class TestGetStashAnalysis:
    def test_parses_stash_with_issue_reference(self):
        stash_show_output = " src/triggers.py | 3 ++-\n 1 file changed, 2 insertions(+), 1 deletion(-)"
        with patch("session_context_triggers.run_git") as mock_git:
            mock_git.side_effect = [
                "stash@{0}: On main: WIP: #931 spec-auditor ground-truth changes\nstash@{1}: On dev: old work",
                stash_show_output,
                "old.py | 1 +\n 1 file changed, 1 insertion(+)",
            ]
            result = get_stash_analysis()
        assert len(result) >= 1
        first = result[0]
        assert first["stash_ref"] == "stash@{0}"
        assert first["branch"] == "main"
        assert first["issue_ref"] == "931"
        assert "spec-auditor" in first["message"]

    def test_parses_stash_without_issue_reference(self):
        stash_list_output = "stash@{0}: On feature/xyz: some work in progress"
        with patch("session_context_triggers.run_git") as mock_git:
            mock_git.side_effect = [stash_list_output, "file.py | 1 +\n 1 file changed, 1 insertion(+)"]
            result = get_stash_analysis()
        assert len(result) == 1
        assert result[0]["issue_ref"] == ""

    def test_returns_empty_when_no_stashes(self):
        with patch("session_context_triggers.run_git", return_value=""):
            result = get_stash_analysis()
        assert result == []

    def test_limits_analysis_to_five_stashes(self):
        stash_lines = [f"stash@{{{i}}}: On dev: work {i}" for i in range(10)]
        stash_list = "\n".join(stash_lines)
        with patch("session_context_triggers.run_git") as mock_git:
            mock_git.side_effect = [stash_list] + ["f.py | 1 +\n 1 file changed"] * 10
            result = get_stash_analysis()
        assert len(result) <= 5


class TestBuildProtectedBranchWarningUpdated:
    def test_includes_diff_summary(self):
        with patch("session_context_triggers.get_current_branch", return_value="dev"):
            with patch(
                "session_context_triggers.get_diff_summary",
                return_value={
                    "file_count": 3,
                    "insertions": 42,
                    "deletions": 7,
                    "key_files": ["src/main.py", "src/triggers.py", "test/test_triggers.py"],
                },
            ):
                result = build_protected_branch_warning(
                    ["M src/main.py", "A src/triggers.py", "M test/test_triggers.py"]
                )
        assert "Protected Branch with Uncommitted Changes" in result
        assert "3 uncommitted changes" in result
        assert "Files changed: 3" in result
        assert "+42 / -7" in result
        assert "Key files:" in result

    def test_no_suggest_line(self):
        with patch("session_context_triggers.get_current_branch", return_value="dev"):
            with patch(
                "session_context_triggers.get_diff_summary",
                return_value={"file_count": 1, "insertions": 5, "deletions": 2, "key_files": ["src/main.py"]},
            ):
                result = build_protected_branch_warning(["M src/main.py"])
        assert "Suggest:" not in result
        assert "Diff summary available" in result

    def test_no_diff_summary_when_none(self):
        with patch("session_context_triggers.get_current_branch", return_value="dev"):
            with patch("session_context_triggers.get_diff_summary", return_value=None):
                result = build_protected_branch_warning(["M src/main.py"])
        assert "Files changed:" not in result
        assert "1 uncommitted changes" in result


class TestBuildStaleStashWarningUpdated:
    def test_includes_stash_analysis(self):
        analyses = [
            {
                "stash_ref": "stash@{0}",
                "branch": "main",
                "message": "WIP: #931 spec-auditor ground-truth changes",
                "issue_ref": "931",
                "file_summary": "src/triggers.py | 3 ++-\n 1 file changed, 2 insertions(+), 1 deletion(-)",
            }
        ]
        with patch("session_context_triggers.get_stash_analysis", return_value=analyses):
            result = build_stale_stash_warning(["stash@{0}: On main: WIP: #931 ..."])
        assert "Stale Stash" in result
        assert "#931" in result
        assert "Related issue:" in result
        assert "branch=main" in result

    def test_no_suggest_line(self):
        with patch("session_context_triggers.get_stash_analysis", return_value=[]):
            result = build_stale_stash_warning(["stash@{0}: On main: old work"])
        assert "Suggest:" not in result
        assert "Stash analysis available" in result

    def test_shows_file_summary(self):
        analyses = [
            {
                "stash_ref": "stash@{0}",
                "branch": "feature",
                "message": "work in progress",
                "issue_ref": "",
                "file_summary": "src/main.py | 2 ++\nsrc/util.py | 4 ++--",
            }
        ]
        with patch("session_context_triggers.get_stash_analysis", return_value=analyses):
            result = build_stale_stash_warning(["stash@{0}: On feature: work in progress"])
        assert "src/main.py" in result


class TestBuildStaleStashWarning:
    def test_warning_output(self):
        result = build_stale_stash_warning(["stash@{0}: On feature: old work"])
        assert "Stale Stash" in result


class TestBuildMergeConflictWarning:
    def test_warning_output(self):
        result = build_merge_conflict_warning(["file1.py"])
        assert "Merge Conflict" in result
        assert "1 unmerged file(s)" in result


class TestBuildUnpushedCommitsWarning:
    def test_warning_output(self):
        result = build_unpushed_commits_warning(5)
        assert "5 commit(s) ahead" in result


class TestBuildOrphanedWorktreesWarning:
    def test_warning_output(self):
        result = build_orphaned_worktrees_warning(["/path/to/wt (branch — merged into dev)"])
        assert "Orphaned Worktrees" in result


class TestTriggersOutput:
    def test_no_identity_in_output(self, tmp_path, capsys):
        with (
            patch("session_context_triggers.get_remote_url", return_value="https://github.com/Org/repo.git"),
            patch("session_context_triggers.get_root_dir", return_value=str(tmp_path)),
            patch("session_context_triggers.is_on_main_branch", return_value=False),
            patch("session_context_triggers.is_on_protected_branch", return_value=False),
            patch("session_context_triggers.has_uncommitted_changes", return_value=(False, [])),
            patch("session_context_triggers.is_pair_mode_branch", return_value=(False, None)),
            patch("session_context_triggers.has_stale_stash", return_value=[]),
            patch("session_context_triggers.has_merge_conflict", return_value=(False, [])),
            patch("session_context_triggers.has_unpushed_commits", return_value=(False, 0)),
            patch("session_context_triggers.has_orphaned_worktrees", return_value=[]),
        ):
            triggers_main()
        captured = capsys.readouterr()
        assert "## Repository Identity" not in captured.out

    def test_main_branch_trigger(self, tmp_path, capsys):
        with (
            patch("session_context_triggers.get_remote_url", return_value="https://github.com/Org/repo.git"),
            patch("session_context_triggers.get_root_dir", return_value=str(tmp_path)),
            patch("session_context_triggers.is_on_main_branch", return_value=True),
            patch("session_context_triggers.is_on_protected_branch", return_value=True),
            patch("session_context_triggers.has_uncommitted_changes", return_value=(False, [])),
            patch("session_context_triggers.is_pair_mode_branch", return_value=(False, None)),
            patch("session_context_triggers.has_stale_stash", return_value=[]),
            patch("session_context_triggers.has_merge_conflict", return_value=(False, [])),
            patch("session_context_triggers.has_unpushed_commits", return_value=(False, 0)),
            patch("session_context_triggers.has_orphaned_worktrees", return_value=[]),
        ):
            triggers_main()
        captured = capsys.readouterr()
        assert "Production Branch" in captured.out

    def test_uncommitted_work_trigger(self, tmp_path, capsys):
        with (
            patch("session_context_triggers.get_remote_url", return_value="https://github.com/Org/repo.git"),
            patch("session_context_triggers.get_root_dir", return_value=str(tmp_path)),
            patch("session_context_triggers.is_on_main_branch", return_value=False),
            patch("session_context_triggers.is_on_protected_branch", return_value=False),
            patch("session_context_triggers.has_uncommitted_changes", return_value=(True, ["M file.py"])),
            patch("session_context_triggers.is_pair_mode_branch", return_value=(False, None)),
            patch("session_context_triggers.has_stale_stash", return_value=[]),
            patch("session_context_triggers.has_merge_conflict", return_value=(False, [])),
            patch("session_context_triggers.has_unpushed_commits", return_value=(False, 0)),
            patch("session_context_triggers.has_orphaned_worktrees", return_value=[]),
        ):
            triggers_main()
        captured = capsys.readouterr()
        assert "Uncommitted Work" in captured.out

    def test_stale_stash_trigger(self, tmp_path, capsys):
        with (
            patch("session_context_triggers.get_remote_url", return_value="https://github.com/Org/repo.git"),
            patch("session_context_triggers.get_root_dir", return_value=str(tmp_path)),
            patch("session_context_triggers.is_on_main_branch", return_value=False),
            patch("session_context_triggers.is_on_protected_branch", return_value=False),
            patch("session_context_triggers.has_uncommitted_changes", return_value=(False, [])),
            patch("session_context_triggers.is_pair_mode_branch", return_value=(False, None)),
            patch("session_context_triggers.has_stale_stash", return_value=["stash@{0}: old stash"]),
            patch("session_context_triggers.has_merge_conflict", return_value=(False, [])),
            patch("session_context_triggers.has_unpushed_commits", return_value=(False, 0)),
            patch("session_context_triggers.has_orphaned_worktrees", return_value=[]),
        ):
            triggers_main()
        captured = capsys.readouterr()
        assert "Stale Stash" in captured.out

    def test_merge_conflict_trigger(self, tmp_path, capsys):
        with (
            patch("session_context_triggers.get_remote_url", return_value="https://github.com/Org/repo.git"),
            patch("session_context_triggers.get_root_dir", return_value=str(tmp_path)),
            patch("session_context_triggers.is_on_main_branch", return_value=False),
            patch("session_context_triggers.is_on_protected_branch", return_value=False),
            patch("session_context_triggers.has_uncommitted_changes", return_value=(False, [])),
            patch("session_context_triggers.is_pair_mode_branch", return_value=(False, None)),
            patch("session_context_triggers.has_stale_stash", return_value=[]),
            patch("session_context_triggers.has_merge_conflict", return_value=(True, ["conflicted.py"])),
            patch("session_context_triggers.has_unpushed_commits", return_value=(False, 0)),
            patch("session_context_triggers.has_orphaned_worktrees", return_value=[]),
        ):
            triggers_main()
        captured = capsys.readouterr()
        assert "Merge Conflict" in captured.out

    def test_unpushed_commits_trigger(self, tmp_path, capsys):
        with (
            patch("session_context_triggers.get_remote_url", return_value="https://github.com/Org/repo.git"),
            patch("session_context_triggers.get_root_dir", return_value=str(tmp_path)),
            patch("session_context_triggers.is_on_main_branch", return_value=False),
            patch("session_context_triggers.is_on_protected_branch", return_value=False),
            patch("session_context_triggers.has_uncommitted_changes", return_value=(False, [])),
            patch("session_context_triggers.is_pair_mode_branch", return_value=(False, None)),
            patch("session_context_triggers.has_stale_stash", return_value=[]),
            patch("session_context_triggers.has_merge_conflict", return_value=(False, [])),
            patch("session_context_triggers.has_unpushed_commits", return_value=(True, 3)),
            patch("session_context_triggers.has_orphaned_worktrees", return_value=[]),
        ):
            triggers_main()
        captured = capsys.readouterr()
        assert "Unpushed Commits" in captured.out

    def test_orphaned_worktrees_trigger(self, tmp_path, capsys):
        with (
            patch("session_context_triggers.get_remote_url", return_value="https://github.com/Org/repo.git"),
            patch("session_context_triggers.get_root_dir", return_value=str(tmp_path)),
            patch("session_context_triggers.is_on_main_branch", return_value=False),
            patch("session_context_triggers.is_on_protected_branch", return_value=False),
            patch("session_context_triggers.has_uncommitted_changes", return_value=(False, [])),
            patch("session_context_triggers.is_pair_mode_branch", return_value=(False, None)),
            patch("session_context_triggers.has_stale_stash", return_value=[]),
            patch("session_context_triggers.has_merge_conflict", return_value=(False, [])),
            patch("session_context_triggers.has_unpushed_commits", return_value=(False, 0)),
            patch("session_context_triggers.has_orphaned_worktrees", return_value=["/path/wt (feat — merged)"]),
        ):
            triggers_main()
        captured = capsys.readouterr()
        assert "Orphaned Worktrees" in captured.out

    def test_pair_mode_trigger(self, tmp_path, capsys):
        with (
            patch("session_context_triggers.get_remote_url", return_value="https://github.com/Org/repo.git"),
            patch("session_context_triggers.get_root_dir", return_value=str(tmp_path)),
            patch("session_context_triggers.is_on_main_branch", return_value=False),
            patch("session_context_triggers.is_on_protected_branch", return_value=False),
            patch("session_context_triggers.has_uncommitted_changes", return_value=(False, [])),
            patch("session_context_triggers.is_pair_mode_branch", return_value=(True, "pair-feature/123-xyz")),
            patch("session_context_triggers.has_stale_stash", return_value=[]),
            patch("session_context_triggers.has_merge_conflict", return_value=(False, [])),
            patch("session_context_triggers.has_unpushed_commits", return_value=(False, 0)),
            patch("session_context_triggers.has_orphaned_worktrees", return_value=[]),
        ):
            triggers_main()
        captured = capsys.readouterr()
        assert "Pair Mode Resumed" in captured.out

    def test_no_triggers_empty_output(self, tmp_path, capsys):
        with (
            patch("session_context_triggers.get_remote_url", return_value="https://github.com/Org/repo.git"),
            patch("session_context_triggers.get_root_dir", return_value=str(tmp_path)),
            patch("session_context_triggers.is_on_main_branch", return_value=False),
            patch("session_context_triggers.is_on_protected_branch", return_value=False),
            patch("session_context_triggers.has_uncommitted_changes", return_value=(False, [])),
            patch("session_context_triggers.is_pair_mode_branch", return_value=(False, None)),
            patch("session_context_triggers.has_stale_stash", return_value=[]),
            patch("session_context_triggers.has_merge_conflict", return_value=(False, [])),
            patch("session_context_triggers.has_unpushed_commits", return_value=(False, 0)),
            patch("session_context_triggers.has_orphaned_worktrees", return_value=[]),
        ):
            triggers_main()
        captured = capsys.readouterr()
        assert captured.out.strip() == ""

    def test_no_respond_directive(self, tmp_path, capsys):
        with (
            patch("session_context_triggers.get_remote_url", return_value="https://github.com/Org/repo.git"),
            patch("session_context_triggers.get_root_dir", return_value=str(tmp_path)),
            patch("session_context_triggers.is_on_main_branch", return_value=True),
            patch("session_context_triggers.is_on_protected_branch", return_value=True),
            patch("session_context_triggers.has_uncommitted_changes", return_value=(True, ["M file.py"])),
            patch("session_context_triggers.is_pair_mode_branch", return_value=(False, None)),
            patch("session_context_triggers.has_stale_stash", return_value=["stash@{0}: old"]),
            patch("session_context_triggers.has_merge_conflict", return_value=(False, [])),
            patch("session_context_triggers.has_unpushed_commits", return_value=(False, 0)),
            patch("session_context_triggers.has_orphaned_worktrees", return_value=[]),
        ):
            triggers_main()
        captured = capsys.readouterr()
        assert "Respond to the above" not in captured.out

    def test_exit_code_0(self, tmp_path):
        with (
            patch("session_context_triggers.get_remote_url", return_value="https://github.com/Org/repo.git"),
            patch("session_context_triggers.get_root_dir", return_value=str(tmp_path)),
            patch("session_context_triggers.is_on_main_branch", return_value=False),
            patch("session_context_triggers.is_on_protected_branch", return_value=False),
            patch("session_context_triggers.has_uncommitted_changes", return_value=(False, [])),
            patch("session_context_triggers.is_pair_mode_branch", return_value=(False, None)),
            patch("session_context_triggers.has_stale_stash", return_value=[]),
            patch("session_context_triggers.has_merge_conflict", return_value=(False, [])),
            patch("session_context_triggers.has_unpushed_commits", return_value=(False, 0)),
            patch("session_context_triggers.has_orphaned_worktrees", return_value=[]),
        ):
            assert triggers_main() == 0

    def test_exit_code_1_no_remote(self):
        with patch("session_context_triggers.get_remote_url", return_value=None):
            assert triggers_main() == 1
