import re
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / ".opencode" / "scripts"))

from session_context_triggers import is_pair_mode_branch


class TestPairModeDetection:
    def test_pair_feature_branch(self):
        with patch.object(subprocess, "run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="pair-feature/123-xyz\n")
            is_pair, branch = is_pair_mode_branch()
            assert is_pair is True
            assert branch == "pair-feature/123-xyz"

    def test_pair_spec_branch(self):
        with patch.object(subprocess, "run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="pair-spec/456-abc\n")
            is_pair, branch = is_pair_mode_branch()
            assert is_pair is True
            assert branch == "pair-spec/456-abc"

    def test_feature_branch_not_pair(self):
        with patch.object(subprocess, "run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="feature/789-xyz\n")
            is_pair, branch = is_pair_mode_branch()
            assert is_pair is False
            assert branch is None

    def test_spec_branch_not_pair(self):
        with patch.object(subprocess, "run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="spec/789-abc\n")
            is_pair, branch = is_pair_mode_branch()
            assert is_pair is False
            assert branch is None

    def test_dev_branch_not_pair(self):
        with patch.object(subprocess, "run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="dev\n")
            is_pair, branch = is_pair_mode_branch()
            assert is_pair is False

    def test_main_branch_not_pair(self):
        with patch.object(subprocess, "run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="main\n")
            is_pair, branch = is_pair_mode_branch()
            assert is_pair is False


class TestPairModeTaskFiles:
    def test_pair_pre_work_task_exists(self):
        path = (
            Path(__file__).resolve().parent.parent
            / ".opencode"
            / "skills"
            / "git-workflow"
            / "tasks"
            / "pair-pre-work.md"
        )
        assert path.is_file(), "pair-pre-work.md must exist"

    def test_pair_commit_task_exists(self):
        path = (
            Path(__file__).resolve().parent.parent
            / ".opencode"
            / "skills"
            / "git-workflow"
            / "tasks"
            / "pair-commit.md"
        )
        assert path.is_file(), "pair-commit.md must exist"

    def test_pair_pr_creation_task_exists(self):
        path = (
            Path(__file__).resolve().parent.parent
            / ".opencode"
            / "skills"
            / "git-workflow"
            / "tasks"
            / "pair-pr-creation.md"
        )
        assert path.is_file(), "pair-pr-creation.md must exist"

    def test_pair_cleanup_task_exists(self):
        path = (
            Path(__file__).resolve().parent.parent
            / ".opencode"
            / "skills"
            / "git-workflow"
            / "tasks"
            / "pair-cleanup.md"
        )
        assert path.is_file(), "pair-cleanup.md must exist"

    def test_pair_mode_resume_task_exists(self):
        path = (
            Path(__file__).resolve().parent.parent
            / ".opencode"
            / "skills"
            / "git-workflow"
            / "tasks"
            / "pair-mode-resume.md"
        )
        assert path.is_file(), "pair-mode-resume.md must exist"


class TestPairModeGuideline:
    def test_guideline_file_exists(self):
        path = Path(__file__).resolve().parent.parent / ".opencode" / "guidelines"
        guideline_files = list(path.glob("*pair*"))
        assert len(guideline_files) > 0, "At least one pair-mode guideline file must exist"

    def test_guideline_mentions_pair_prefix(self):
        path = Path(__file__).resolve().parent.parent / ".opencode" / "guidelines"
        guideline_files = list(path.glob("*pair*"))
        if guideline_files:
            content = guideline_files[0].read_text()
            assert "pair-" in content, "Pair mode guideline must mention pair- prefix"


class TestSessionContextPairModeResume:
    def test_issue_number_inference_from_branch(self):
        branch = "pair-feature/123-xyz"
        match = re.search(r"/(\d+)[-/]", branch)
        assert match is not None, "Must extract issue number from pair-feature branch"
        assert match.group(1) == "123"

    def test_no_issue_number_in_branch(self):
        branch = "pair-feature/xyz"
        match = re.search(r"/(\d+)[-/]", branch)
        assert match is None, "Branch without issue number should not match"

    def test_spec_branch_issue_number(self):
        branch = "pair-spec/456-abc"
        match = re.search(r"/(\d+)[-/]", branch)
        assert match is not None
        assert match.group(1) == "456"
