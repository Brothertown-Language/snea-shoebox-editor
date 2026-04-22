"""Tests for session trigger behavior contract.

Verifies that trigger output format drives correct agent behavior:
- No "Suggest:" text in trigger output (replaced by structured data)
- Structured data present for actionable triggers
- Trigger types that should be suppressed produce no echo-friendly text
"""

import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / ".opencode" / "scripts"))

from session_context_triggers import (
    build_main_branch_warning,
    build_merge_conflict_warning,
    build_orphaned_worktrees_warning,
    build_protected_branch_warning,
    build_stale_stash_warning,
    build_uncommitted_work_warning,
    build_unpushed_commits_warning,
)

TRIGGER_BUILDERS = [
    "build_main_branch_warning",
    "build_protected_branch_warning",
    "build_stale_stash_warning",
    "build_merge_conflict_warning",
    "build_unpushed_commits_warning",
    "build_orphaned_worktrees_warning",
]


class TestNoSuggestLineInAnyTrigger:
    def test_protected_branch_no_suggest(self):
        with patch("session_context_triggers.get_current_branch", return_value="dev"):
            with patch(
                "session_context_triggers.get_diff_summary",
                return_value={"file_count": 1, "insertions": 5, "deletions": 2, "key_files": ["src/main.py"]},
            ):
                result = build_protected_branch_warning(["M src/main.py"])
        assert "Suggest:" not in result

    def test_stale_stash_no_suggest(self):
        with patch("session_context_triggers.get_stash_analysis", return_value=[]):
            result = build_stale_stash_warning(["stash@{0}: On main: old work"])
        assert "Suggest:" not in result

    def test_uncommitted_work_no_suggest(self):
        result = build_uncommitted_work_warning(["file1.py"])
        assert "Suggest:" not in result

    def test_main_branch_no_suggest(self):
        result = build_main_branch_warning(True, ["M file.py"])
        assert "Suggest:" not in result

    def test_merge_conflict_no_suggest(self):
        result = build_merge_conflict_warning(["conflicted.py"])
        assert "Suggest:" not in result

    def test_unpushed_commits_no_suggest(self):
        result = build_unpushed_commits_warning(3)
        assert "Suggest:" not in result

    def test_orphaned_worktrees_no_suggest(self):
        result = build_orphaned_worktrees_warning(["/path/wt (feat — merged)"])
        assert "Suggest:" not in result


class TestProtectedBranchOutputContainsDiffSummary:
    def test_includes_diff_summary_section(self):
        with patch("session_context_triggers.get_current_branch", return_value="dev"):
            with patch(
                "session_context_triggers.get_diff_summary",
                return_value={
                    "file_count": 3,
                    "insertions": 20,
                    "deletions": 5,
                    "key_files": ["src/a.py", "src/b.py", "test/test_c.py"],
                },
            ):
                result = build_protected_branch_warning(["M src/a.py", "M src/b.py", "M test/test_c.py"])
        assert "Files changed:" in result
        assert "+20 / -5" in result

    def test_diff_summary_available_indicator(self):
        with patch("session_context_triggers.get_current_branch", return_value="dev"):
            with patch(
                "session_context_triggers.get_diff_summary",
                return_value={"file_count": 1, "insertions": 3, "deletions": 0, "key_files": ["src/x.py"]},
            ):
                result = build_protected_branch_warning(["M src/x.py"])
        assert "Diff summary available" in result


class TestStaleStashOutputContainsAnalysis:
    def test_includes_stash_analysis_indicator(self):
        with patch("session_context_triggers.get_stash_analysis", return_value=[]):
            result = build_stale_stash_warning(["stash@{0}: On main: old"])
        assert "Stash analysis available" in result

    def test_includes_issue_reference(self):
        analyses = [
            {
                "stash_ref": "stash@{0}",
                "branch": "main",
                "message": "WIP: #931 changes",
                "issue_ref": "931",
                "file_summary": "f.py | 1 +",
            }
        ]
        with patch("session_context_triggers.get_stash_analysis", return_value=analyses):
            result = build_stale_stash_warning(["stash@{0}: On main: WIP: #931 changes"])
        assert "#931" in result


class TestTriggerOutputIsMachineReadable:
    def test_protected_branch_uses_structured_headers(self):
        with patch("session_context_triggers.get_current_branch", return_value="dev"):
            with patch(
                "session_context_triggers.get_diff_summary",
                return_value={"file_count": 1, "insertions": 2, "deletions": 1, "key_files": ["src/f.py"]},
            ):
                result = build_protected_branch_warning(["M src/f.py"])
        assert result.startswith("## Protected Branch")
        for line in result.splitlines():
            if line.strip().startswith("- ") and "Branch:" not in line and "Key files:" not in line:
                assert ": " in line or line.strip().startswith("- `"), f"Line not structured: {line}"

    def test_stale_stash_uses_structured_headers(self):
        analyses = [
            {
                "stash_ref": "stash@{0}",
                "branch": "dev",
                "message": "work",
                "issue_ref": "",
                "file_summary": "a.py | 1 +",
            }
        ]
        with patch("session_context_triggers.get_stash_analysis", return_value=analyses):
            result = build_stale_stash_warning(["stash@{0}: On dev: work"])
        assert result.startswith("## Stale Stash")
        assert "branch=" in result
