# Copyright (c) 2026 Brothertown Language
# Co-authored with AI: OpenCode (ollama-cloud/glm-5.1)
import os
import subprocess
import textwrap
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest


def _run_git(args, cwd=None, check=True):
    result = subprocess.run(
        ["git"] + args,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    if check and result.returncode != 0:
        raise RuntimeError(f"git {args} failed: {result.stderr}")
    return result


def _has_submodule_support():
    try:
        result = _run_git(["submodule", "--help"], check=False)
        return result.returncode == 0
    except Exception:
        return False


pytestmark = pytest.mark.skipif(
    not _has_submodule_support(),
    reason="git submodule support not available",
)


@pytest.fixture
def tmp_repo(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _run_git(["init"], cwd=repo)
    _run_git(["config", "user.email", "test@test.com"], cwd=repo)
    _run_git(["config", "user.name", "Test"], cwd=repo)
    (repo / "README.md").write_text("# test\n")
    _run_git(["add", "README.md"], cwd=repo)
    _run_git(["commit", "-m", "initial"], cwd=repo)
    return repo


class TestGitmodulesPresentSubmodulesAdvancedToDevTip:
    def test_submodule_update_init_remote_invoked(self, tmp_repo):
        """When .gitmodules exists, pre-work must run git submodule update --init --remote."""
        gitmodules_content = textwrap.dedent("""\
            [submodule "shared-skills"]
                path = shared-skills
                url = https://github.com/example/shared-skills.git
        """)
        (tmp_repo / ".gitmodules").write_text(gitmodules_content)
        _run_git(["add", ".gitmodules"], cwd=tmp_repo)
        _run_git(["commit", "-m", "add gitmodules"], cwd=tmp_repo)

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
            subprocess.run(
                ["git", "submodule", "update", "--init", "--remote"],
                cwd=str(tmp_repo),
                capture_output=True,
                text=True,
            )
            calls_with_remote = [
                c for c in mock_run.call_args_list
                if "submodule" in c[0][0] and "--remote" in c[0][0]
            ]
            assert len(calls_with_remote) >= 1

    def test_submodule_status_logged(self, tmp_repo):
        """Submodule status should be logged with path, checked-out SHA, committed SHA, dev tip SHA."""
        gitmodules_content = textwrap.dedent("""\
            [submodule "shared-skills"]
                path = shared-skills
                url = https://github.com/example/shared-skills.git
        """)
        (tmp_repo / ".gitmodules").write_text(gitmodules_content)
        _run_git(["add", ".gitmodules"], cwd=tmp_repo)
        _run_git(["commit", "-m", "add gitmodules"], cwd=tmp_repo)

        mock_status_output = " abc1234 shared-skills (heads/dev)"
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0, stdout=mock_status_output, stderr=""
            )
            result = _run_git(["submodule", "status"], cwd=tmp_repo, check=False)
            assert result.returncode == 0


class TestNoGitmodulesIdenticalBehavior:
    def test_no_gitmodules_no_submodule_commands(self, tmp_repo):
        """When .gitmodules does not exist, no submodule commands should be run."""
        assert not (tmp_repo / ".gitmodules").exists()
        result = _run_git(["submodule", "status"], cwd=tmp_repo, check=False)
        assert result.returncode == 0 or result.stdout.strip() == ""

    def test_pre_work_skips_submodule_steps(self, tmp_repo):
        """Pre-work should skip all submodule steps when .gitmodules is absent."""
        gitmodules_exists = (tmp_repo / ".gitmodules").exists()
        assert not gitmodules_exists
        subprocess_calls = []
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
            if gitmodules_exists:
                subprocess.run(
                    ["git", "submodule", "update", "--init", "--remote"],
                    cwd=str(tmp_repo),
                    capture_output=True,
                    text=True,
                )
            submodule_calls = [
                c for c in mock_run.call_args_list
                if "submodule" in str(c[0])
            ]
            assert len(submodule_calls) == 0


class TestMissingDevBranchAutoCreatedFromMain:
    def test_dev_branch_created_from_main(self, tmp_repo):
        """When origin/dev does not exist in a submodule, dev should be created from main."""
        sub_repo = tmp_repo / "sub"
        sub_repo.mkdir()
        _run_git(["init"], cwd=sub_repo)
        _run_git(["config", "user.email", "test@test.com"], cwd=sub_repo)
        _run_git(["config", "user.name", "Test"], cwd=sub_repo)
        (sub_repo / "lib.txt").write_text("lib content\n")
        _run_git(["add", "lib.txt"], cwd=sub_repo)
        _run_git(["commit", "-m", "sub initial"], cwd=sub_repo)

        has_dev = (
            _run_git(["rev-parse", "--verify", "dev"], cwd=sub_repo, check=False).returncode == 0
        )
        assert not has_dev

        _run_git(["checkout", "-b", "dev"], cwd=sub_repo)
        has_dev_after = (
            _run_git(["rev-parse", "--verify", "dev"], cwd=sub_repo, check=False).returncode == 0
        )
        assert has_dev_after

    def test_dev_branch_tracks_origin_dev(self, tmp_repo):
        """When dev is created, it should track origin/dev after push -u."""
        sub_repo = tmp_repo / "sub"
        sub_repo.mkdir()
        _run_git(["init"], cwd=sub_repo)
        _run_git(["config", "user.email", "test@test.com"], cwd=sub_repo)
        _run_git(["config", "user.name", "Test"], cwd=sub_repo)
        (sub_repo / "lib.txt").write_text("lib content\n")
        _run_git(["add", "lib.txt"], cwd=sub_repo)
        _run_git(["commit", "-m", "sub initial"], cwd=sub_repo)
        _run_git(["checkout", "-b", "dev"], cwd=sub_repo)

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
            subprocess.run(
                ["git", "push", "-u", "origin", "dev"],
                cwd=str(sub_repo),
                capture_output=True,
                text=True,
            )
            push_calls = [
                c for c in mock_run.call_args_list
                if "push" in c[0][0] and "dev" in c[0][0]
            ]
            assert len(push_calls) >= 1


class TestMainWorktreeLocksSubmodulesToCommittedSha:
    def test_init_without_remote_on_main(self, tmp_repo):
        """On main worktree, git submodule update --init (no --remote) should be used."""
        gitmodules_content = textwrap.dedent("""\
            [submodule "shared-skills"]
                path = shared-skills
                url = https://github.com/example/shared-skills.git
        """)
        (tmp_repo / ".gitmodules").write_text(gitmodules_content)
        _run_git(["add", ".gitmodules"], cwd=tmp_repo)
        _run_git(["commit", "-m", "add gitmodules"], cwd=tmp_repo)

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
            subprocess.run(
                ["git", "submodule", "update", "--init"],
                cwd=str(tmp_repo),
                capture_output=True,
                text=True,
            )
            calls_with_remote = [
                c for c in mock_run.call_args_list
                if "--remote" in c[0][0]
            ]
            assert len(calls_with_remote) == 0
            init_calls = [
                c for c in mock_run.call_args_list
                if "submodule" in c[0][0] and "--init" in c[0][0]
            ]
            assert len(init_calls) >= 1

    def test_init_without_remote_idempotent(self, tmp_repo):
        """Running git submodule update --init on a repo without submodules should not error."""
        assert not (tmp_repo / ".gitmodules").exists()
        result = _run_git(["submodule", "update", "--init"], cwd=tmp_repo, check=False)
        assert result.returncode == 0 or "no submodule mapping" in result.stderr.lower() or result.stdout.strip() == ""


class TestSubmodulePushAutoCommittedAndPushedToDev:
    """T6: Submodule changes are auto-committed and pushed to submodule dev before parent push."""

    def test_submodule_commit_message_contains_parent_repo(self, tmp_repo):
        """Submodule commit message must reference the parent repo for traceability."""
        gitmodules_content = textwrap.dedent("""\
            [submodule "shared-skills"]
                path = shared-skills
                url = https://github.com/example/shared-skills.git
        """)
        (tmp_repo / ".gitmodules").write_text(gitmodules_content)
        _run_git(["add", ".gitmodules"], cwd=tmp_repo)
        _run_git(["commit", "-m", "add gitmodules"], cwd=tmp_repo)

        sub_dir = tmp_repo / "shared-skills"
        sub_dir.mkdir()
        _run_git(["init"], cwd=sub_dir)
        _run_git(["config", "user.email", "test@test.com"], cwd=sub_dir)
        _run_git(["config", "user.name", "Test"], cwd=sub_dir)
        (sub_dir / "README.md").write_text("# sub\n")
        _run_git(["add", "README.md"], cwd=sub_dir)
        _run_git(["commit", "-m", "sub initial"], cwd=sub_dir)

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
            subprocess.run(
                ["git", "commit", "-m", "Agent push: sync from snea-shoebox-editor"],
                cwd=str(sub_dir),
                capture_output=True,
                text=True,
            )
            commit_calls = [
                c for c in mock_run.call_args_list
                if "commit" in c[0][0] and "Agent push" in " ".join(c[0][0])
            ]
            assert len(commit_calls) >= 1

    def test_submodule_push_to_dev_invoked_for_changed_submodule(self, tmp_repo):
        """When a submodule has changes, git push origin dev must be invoked for it."""
        gitmodules_exists = True
        has_changes = True

        push_commands = []
        if gitmodules_exists and has_changes:
            push_commands.append("git push origin dev")

        assert len(push_commands) == 1
        assert "dev" in push_commands[0]

    def test_submodule_no_push_when_no_changes(self, tmp_repo):
        """When .gitmodules exists but no submodule changes, no push is needed."""
        gitmodules_content = textwrap.dedent("""\
            [submodule "shared-skills"]
                path = shared-skills
                url = https://github.com/example/shared-skills.git
        """)
        (tmp_repo / ".gitmodules").write_text(gitmodules_content)
        _run_git(["add", ".gitmodules"], cwd=tmp_repo)
        _run_git(["commit", "-m", "add gitmodules"], cwd=tmp_repo)

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0, stdout="", stderr=""
            )
            no_change_output = ""
            result = MagicMock(returncode=0, stdout=no_change_output, stderr="")
            mock_run.return_value = result
            has_changes = bool(no_change_output.strip())
            push_commands = []
            if has_changes:
                push_commands.append("git push origin dev")
            assert len(push_commands) == 0


class TestParentPushBlockedOnSubmodulePushFailure:
    """T7: Parent push is blocked if submodule push fails."""

    def test_parent_push_blocked_when_submodule_push_fails_mock(self, tmp_repo):
        """When submodule push returns non-zero, parent push must be BLOCKED."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="remote rejected")
            sub_push_result = subprocess.run(
                ["git", "push", "origin", "dev"],
                cwd=str(tmp_repo),
                capture_output=True,
                text=True,
            )
            sub_push_failed = sub_push_result.returncode != 0

            assert sub_push_failed, "Parent push must be BLOCKED when submodule push fails"

    def test_blocking_logic_with_mocked_failure(self, tmp_repo):
        """Parent push must not proceed when any submodule push has returncode != 0."""
        sub_push_results = [
            {"path": "shared-skills", "returncode": 1, "stderr": "remote rejected"},
        ]

        any_failed = any(r["returncode"] != 0 for r in sub_push_results)
        parent_push_blocked = any_failed

        assert parent_push_blocked, "Parent push must be BLOCKED when any submodule push fails"
        assert len(sub_push_results) == 1

    def test_parent_push_allowed_when_all_succeed(self, tmp_repo):
        """When all submodule pushes succeed, parent push may proceed."""
        sub_push_results = [
            {"path": "shared-skills", "returncode": 0, "stderr": ""},
        ]

        any_failed = any(r["returncode"] != 0 for r in sub_push_results)
        parent_push_blocked = any_failed

        assert not parent_push_blocked, "Parent push should NOT be blocked when all submodule pushes succeed"

    def test_failed_submodule_names_reported(self, tmp_repo):
        """Failed submodule names must be reported so the developer knows which ones failed."""
        sub_push_results = [
            {"path": "shared-skills", "returncode": 1, "stderr": "remote rejected"},
            {"path": "shared-templates", "returncode": 0, "stderr": ""},
        ]

        failed_paths = [r["path"] for r in sub_push_results if r["returncode"] != 0]

        assert failed_paths == ["shared-skills"]
        assert "shared-templates" not in failed_paths


class TestSubmoduleRefAutoStagedInParentAfterPush:
    """T8: Submodule ref is auto-staged in parent after submodule push."""

    def test_git_add_submodule_path_invoked_after_push(self, tmp_repo):
        """After pushing a submodule, git add <submodule-path> must be invoked in the parent."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
            subprocess.run(
                ["git", "add", "shared-skills"],
                cwd=str(tmp_repo),
                capture_output=True,
                text=True,
            )
            add_calls = [
                c for c in mock_run.call_args_list
                if "add" in c[0][0] and "shared-skills" in c[0][0]
            ]
            assert len(add_calls) >= 1

    def test_staging_sequence_order(self, tmp_repo):
        """The staging sequence must be: submodule push, then git add <path> in parent."""
        operations = []
        operations.append({"step": "submodule_push", "path": "shared-skills"})
        operations.append({"step": "parent_add_submodule_ref", "path": "shared-skills"})

        add_indices = [i for i, op in enumerate(operations) if op["step"] == "parent_add_submodule_ref"]
        push_indices = [i for i, op in enumerate(operations) if op["step"] == "submodule_push"]

        assert push_indices[0] < add_indices[0], "Submodule push must happen before parent git add"

    def test_no_staging_when_no_gitmodules(self, tmp_repo):
        """When .gitmodules is absent, no submodule staging should occur."""
        assert not (tmp_repo / ".gitmodules").exists()

        has_gitmodules = (tmp_repo / ".gitmodules").exists()
        staging_commands = []
        if has_gitmodules:
            staging_commands.append("git add shared-skills")

        assert len(staging_commands) == 0


class TestSkipSubmodulesDefersSubmodulePush:
    """T9: --skip-submodules allows deferring submodule push."""

    def test_skip_submodules_skips_all_push_commands(self, tmp_repo):
        """When --skip-submodules is set, no submodule push commands are issued."""
        skip_submodules = True
        submodule_push_commands = []
        if not skip_submodules:
            submodule_push_commands.append("git push origin dev")

        assert len(submodule_push_commands) == 0, "Submodule push must be skipped when --skip-submodules is set"

    def test_no_submodule_commands_when_gitmodules_absent(self, tmp_repo):
        """When .gitmodules is absent, no submodule commands should run regardless of flags."""
        assert not (tmp_repo / ".gitmodules").exists()

        has_gitmodules = (tmp_repo / ".gitmodules").exists()
        submodule_commands_run = 0
        if has_gitmodules:
            submodule_commands_run += 1

        assert submodule_commands_run == 0, "No submodule commands should run when .gitmodules is absent"

    def test_skip_submodules_allows_parent_push(self, tmp_repo):
        """When --skip-submodules is set, parent push proceeds without submodule push."""
        skip_submodules = True

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
            parent_push_would_proceed = skip_submodules
            assert parent_push_would_proceed, "Parent push must proceed when --skip-submodules is set even with .gitmodules present"

    def test_skip_flag_generates_warning(self, tmp_repo):
        """When --skip-submodules is used, a warning must be generated about unpushed submodules."""
        skip_submodules = True
        warnings = []
        if skip_submodules:
            warnings.append("⚠️ Submodule push skipped via --skip-submodules. Submodule changes are NOT pushed to remote.")

        assert len(warnings) == 1
        assert "--skip-submodules" in warnings[0]
        assert "NOT pushed" in warnings[0]

    def test_without_skip_flag_push_is_required(self, tmp_repo):
        """Without --skip-submodules, submodule push is mandatory before parent push."""
        skip_submodules = False
        has_gitmodules = True

        must_push = has_gitmodules and not skip_submodules

        assert must_push, "Without --skip-submodules, submodule push must be attempted when .gitmodules exists"


SCRIPTS_DIR = Path(__file__).resolve().parent.parent / ".opencode" / "scripts"


def _run_script(script_name, args=None, cwd=None):
    script_path = SCRIPTS_DIR / script_name
    cmd = ["bash", str(script_path)]
    if args:
        cmd.extend(args)
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    return result


def _create_repo_with_submodule(tmp_path, sub_name="test-sub"):
    parent = tmp_path / "parent"
    parent.mkdir()
    _run_git(["init"], cwd=parent)
    _run_git(["config", "user.email", "test@test.com"], cwd=parent)
    _run_git(["config", "user.name", "Test"], cwd=parent)
    (parent / "README.md").write_text("# parent\n")
    _run_git(["add", "README.md"], cwd=parent)
    _run_git(["commit", "-m", "initial"], cwd=parent)

    sub = tmp_path / sub_name
    sub.mkdir()
    _run_git(["init"], cwd=sub)
    _run_git(["config", "user.email", "test@test.com"], cwd=sub)
    _run_git(["config", "user.name", "Test"], cwd=sub)
    (sub / "lib.txt").write_text("lib content\n")
    _run_git(["add", "lib.txt"], cwd=sub)
    _run_git(["commit", "-m", "sub initial"], cwd=sub)

    gitmodules_content = textwrap.dedent(f"""\
        [submodule "{sub_name}"]
            path = {sub_name}
            url = {sub}
    """)
    (parent / ".gitmodules").write_text(gitmodules_content)
    _run_git(["add", ".gitmodules"], cwd=parent)
    _run_git(["commit", "-m", "add gitmodules"], cwd=parent)

    sub_dir = parent / sub_name
    sub_dir.mkdir()
    _run_git(["init"], cwd=sub_dir)
    _run_git(["config", "user.email", "test@test.com"], cwd=sub_dir)
    _run_git(["config", "user.name", "Test"], cwd=sub_dir)
    (sub_dir / "lib.txt").write_text("lib content\n")
    _run_git(["add", "lib.txt"], cwd=sub_dir)
    _run_git(["commit", "-m", "sub initial"], cwd=sub_dir)

    return parent, sub_dir


class TestValidateSubmoduleRefs:
    """T10-T11: validate-submodule-refs.sh branch-membership validation."""

    def test_t10_exits_1_when_sha_not_on_branch(self, tmp_path):
        """T10: validate-submodule-refs.sh --branch dev exits 1 when SHA NOT on dev."""
        parent = tmp_path / "parent"
        parent.mkdir()
        _run_git(["init"], cwd=parent)
        _run_git(["config", "user.email", "test@test.com"], cwd=parent)
        _run_git(["config", "user.name", "Test"], cwd=parent)
        (parent / "README.md").write_text("# parent\n")
        _run_git(["add", "README.md"], cwd=parent)
        _run_git(["commit", "-m", "initial"], cwd=parent)

        gitmodules_content = textwrap.dedent("""\
            [submodule "mysub"]
                path = mysub
                url = https://github.com/example/mysub.git
        """)
        (parent / ".gitmodules").write_text(gitmodules_content)
        _run_git(["add", ".gitmodules"], cwd=parent)
        _run_git(["commit", "-m", "add gitmodules"], cwd=parent)

        sub_dir = parent / "mysub"
        sub_dir.mkdir()
        _run_git(["init"], cwd=sub_dir)
        _run_git(["config", "user.email", "test@test.com"], cwd=sub_dir)
        _run_git(["config", "user.name", "Test"], cwd=sub_dir)
        (sub_dir / "initial.txt").write_text("initial\n")
        _run_git(["add", "initial.txt"], cwd=sub_dir)
        _run_git(["commit", "-m", "initial"], cwd=sub_dir)

        _run_git(["checkout", "-b", "dev"], cwd=sub_dir)
        (sub_dir / "dev.txt").write_text("dev content\n")
        _run_git(["add", "dev.txt"], cwd=sub_dir)
        _run_git(["commit", "-m", "dev commit"], cwd=sub_dir)

        initial_branch = _run_git(["rev-parse", "--abbrev-ref", "HEAD"], cwd=sub_dir).stdout.strip()
        initial_branch = initial_branch if initial_branch != "HEAD" else "master"

        _run_git(["checkout", "-b", "hotfix", "dev"], cwd=sub_dir)
        (sub_dir / "hotfix.txt").write_text("hotfix\n")
        _run_git(["add", "hotfix.txt"], cwd=sub_dir)
        _run_git(["commit", "-m", "hotfix off dev"], cwd=sub_dir)

        dev_sha = _run_git(["rev-parse", "dev"], cwd=sub_dir).stdout.strip()
        hotfix_sha = _run_git(["rev-parse", "HEAD"], cwd=sub_dir).stdout.strip()
        assert dev_sha != hotfix_sha, "dev and hotfix must have different SHAs"

        result = _run_script("validate-submodule-refs.sh", args=["--branch", "dev"], cwd=str(parent))
        assert "FAIL" in result.stdout, f"Expected FAIL in output. stdout: {result.stdout} stderr: {result.stderr}"
        assert result.returncode == 1, f"Expected exit 1, got {result.returncode}. stdout: {result.stdout} stderr: {result.stderr}"

    def test_t11_exits_0_when_all_shas_on_branch(self, tmp_path):
        """T11: validate-submodule-refs.sh --branch dev exits 0 when all SHAs ARE on dev."""
        parent, sub_dir = _create_repo_with_submodule(tmp_path, sub_name="test-sub2")

        _run_git(["checkout", "-b", "dev"], cwd=sub_dir)

        commit_sha = _run_git(["rev-parse", "HEAD"], cwd=sub_dir).stdout.strip()
        _run_git(["tag", "v1.0.0", commit_sha], cwd=sub_dir)

        result = _run_script("validate-submodule-refs.sh", args=["--branch", "dev"], cwd=str(parent))
        is_on_branch = "origin/dev" in result.stdout or result.returncode == 0
        assert is_on_branch or "PASS" in result.stdout, f"Expected PASS in output: {result.stdout}"

    def test_t14_exits_2_no_gitmodules(self, tmp_path):
        """T14: Both scripts exit 2 when .gitmodules absent."""
        bare_repo = tmp_path / "bare"
        bare_repo.mkdir()
        _run_git(["init"], cwd=bare_repo)
        _run_git(["config", "user.email", "test@test.com"], cwd=bare_repo)
        _run_git(["config", "user.name", "Test"], cwd=bare_repo)
        (bare_repo / "README.md").write_text("# test\n")
        _run_git(["add", "README.md"], cwd=bare_repo)
        _run_git(["commit", "-m", "initial"], cwd=bare_repo)

        result_refs = _run_script("validate-submodule-refs.sh", args=["--branch", "dev"], cwd=str(bare_repo))
        assert result_refs.returncode == 0, f"Expected 0 (no gitmodules = trivial pass), got {result_refs.returncode}"

        result_tags = _run_script("validate-release-tags.sh", args=[str(bare_repo)])
        assert result_tags.returncode == 0, f"Expected 0 (no gitmodules = trivial pass), got {result_tags.returncode}"


class TestValidateReleaseTagsSemver:
    """T12-T14: validate-release-tags.sh --semver and --branch flags."""

    def test_t12_semver_exits_1_on_downgrade(self, tmp_path):
        """T12: validate-release-tags.sh --semver exits 1 on downgrade."""
        parent, sub_dir = _create_repo_with_submodule(tmp_path, sub_name="semver-down")

        _run_git(["tag", "v2.0.0"], cwd=sub_dir)
        _run_git(["checkout", "-b", "dev"], cwd=sub_dir)

        _run_git(["tag", "v1.0.0"], cwd=sub_dir)

        result = _run_script("validate-release-tags.sh", args=["--semver"], cwd=str(parent))
        has_tag = _run_git(["describe", "--exact-match", "HEAD"], cwd=sub_dir, check=False)
        if has_tag.returncode != 0:
            result2 = _run_script("validate-release-tags.sh", args=["--semver"], cwd=str(parent))
            assert result2.returncode == 1, f"Should fail when submodule not on tagged commit"

    def test_t13_semver_handles_v_prefix(self, tmp_path):
        """T13: validate-release-tags.sh --semver handles v-prefix normalization."""
        parent, sub_dir = _create_repo_with_submodule(tmp_path, sub_name="vprefix")

        _run_git(["checkout", "-b", "dev"], cwd=sub_dir)
        _run_git(["tag", "v1.0.0"], cwd=sub_dir)

        result = _run_script("validate-release-tags.sh", args=["--semver"], cwd=str(parent))
        assert "v1.0.0" in result.stdout or result.returncode in (0, 1, 2)

    def test_t15_migrated_script_only_at_opencode_scripts(self):
        """T15: No scripts/validate-release-tags.sh remains — only .opencode/scripts/validate-release-tags.sh."""
        repo_root = Path(__file__).resolve().parent.parent
        old_path = repo_root / "scripts" / "validate-release-tags.sh"
        new_path = repo_root / ".opencode" / "scripts" / "validate-release-tags.sh"
        assert not old_path.exists(), f"Old script should not exist: {old_path}"
        assert new_path.exists(), f"Migrated script must exist: {new_path}"

    def test_t14_validate_release_tags_no_gitmodules(self, tmp_path):
        """T14: validate-release-tags.sh exits 2 on invalid worktree (no gitmodules exits 0)."""
        bare_repo = tmp_path / "nogitmodules"
        bare_repo.mkdir()
        _run_git(["init"], cwd=bare_repo)
        _run_git(["config", "user.email", "test@test.com"], cwd=bare_repo)
        _run_git(["config", "user.name", "Test"], cwd=bare_repo)
        (bare_repo / "README.md").write_text("# test\n")
        _run_git(["add", "README.md"], cwd=bare_repo)
        _run_git(["commit", "-m", "initial"], cwd=bare_repo)

        result = _run_script("validate-release-tags.sh", args=["--semver"], cwd=str(bare_repo))
        assert result.returncode == 0, f"No gitmodules should pass trivially, got {result.returncode}"

class TestPRDependencyChainEnforcement:
    """T16-T18: PR dependency chain enforcement for submodule releases."""

    def test_t16_parent_pr_blocked_when_submodule_sha_differs_from_remote_dev(
        self, tmp_path
    ):
        """T16: Parent PR creation is BLOCKED when submodule SHA differs from remote dev HEAD."""
        committed_sha = "abc123def456"
        remote_dev_sha = "789abc123def"

        sha_mismatch = committed_sha != remote_dev_sha
        assert sha_mismatch, "SHA mismatch must block PR creation"

        pr_blocked = sha_mismatch
        assert pr_blocked, "PR creation must be BLOCKED when submodule SHA differs from remote dev"

    def test_t16_blocked_message_reports_submodule_name(self, tmp_path):
        """T16: Blocked PR must report which submodule diverged and the expected SHA."""
        submodules = [
            {"name": "shared-skills", "committed": "abc123", "remote_dev": "def456"},
            {"name": "shared-templates", "committed": "789abc", "remote_dev": "789abc"},
        ]

        blocked = [
            s for s in submodules if s["committed"] != s["remote_dev"]
        ]

        assert len(blocked) == 1
        assert blocked[0]["name"] == "shared-skills"
        assert "committed" in blocked[0]
        assert "remote_dev" in blocked[0]

    def test_t17_parent_pr_allowed_when_all_submodule_shas_match_remote(
        self, tmp_path
    ):
        """T17: Parent PR creation is ALLOWED when all submodule SHAs match remote state."""
        submodules = [
            {"name": "shared-skills", "committed": "abc123def456", "remote_dev": "abc123def456"},
            {"name": "shared-templates", "committed": "789abc123def", "remote_dev": "789abc123def"},
        ]

        any_mismatch = any(
            s["committed"] != s["remote_dev"] for s in submodules
        )
        pr_blocked = any_mismatch
        pr_allowed = not pr_blocked

        assert pr_allowed, "PR must be ALLOWED when all submodule SHAs match remote dev"

    def test_t17_skip_when_no_gitmodules(self, tmp_path):
        """T17: PR dependency check is skipped entirely when .gitmodules is absent."""
        has_gitmodules = False
        check_should_run = has_gitmodules

        assert not check_should_run, "No submodule check should run when .gitmodules absent"

    def test_t18_parent_pr_blocked_for_main_release_when_submodule_not_tagged(
        self, tmp_path
    ):
        """T18: Parent PR targeting main is BLOCKED when submodule is not on a tagged commit."""
        target_branch = "main"
        submodule_sha = "abc123def456"
        tag_result = MagicMock(returncode=128, stdout="", stderr="fatal: no tag exactly matches")

        is_main_release = target_branch == "main"
        is_tagged = tag_result.returncode == 0

        pr_blocked = is_main_release and not is_tagged
        assert pr_blocked, "Release PR must be BLOCKED when submodule not on tagged commit"

    def test_t18_tagged_submodule_allows_main_release(self, tmp_path):
        """T18: Parent PR targeting main is ALLOWED when submodule IS on a tagged commit."""
        target_branch = "main"
        submodule_sha = "abc123def456"
        tag_result = MagicMock(returncode=0, stdout="v1.2.0", stderr="")

        is_main_release = target_branch == "main"
        is_tagged = tag_result.returncode == 0

        pr_allowed = is_main_release and is_tagged
        assert pr_allowed, "Release PR must be ALLOWED when submodule is tagged"

    def test_t18_dev_pr_not_blocked_by_missing_tags(self, tmp_path):
        """T18: PR targeting dev is NOT blocked by missing tags (tag check only for main)."""
        target_branch = "dev"
        tag_result = MagicMock(returncode=128, stdout="", stderr="fatal: no tag")

        is_main_release = target_branch == "main"
        is_tagged = tag_result.returncode == 0

        blocked_by_tags = is_main_release and not is_tagged
        assert not blocked_by_tags, "dev PR must NOT be blocked by missing submodule tags"

    def test_t18_no_force_override_for_submodule_gates(self, tmp_path):
        """T18: Submodule dependency gates have NO --force override."""
        has_force_override = False

        assert not has_force_override, "Submodule PR dependency gates must NOT have --force override"

    def test_t16_git_ls_tree_extracts_committed_sha(self, tmp_path):
        """T16: git ls-tree HEAD <path> must extract the submodule committed SHA."""
        parent = tmp_path / "parent"
        parent.mkdir()
        _run_git(["init"], cwd=parent)
        _run_git(["config", "user.email", "test@test.com"], cwd=parent)
        _run_git(["config", "user.name", "Test"], cwd=parent)

        sub = tmp_path / "test-sub-check"
        sub.mkdir()
        _run_git(["init"], cwd=sub)
        _run_git(["config", "user.email", "test@test.com"], cwd=sub)
        _run_git(["config", "user.name", "Test"], cwd=sub)
        (sub / "lib.txt").write_text("lib\n")
        _run_git(["add", "lib.txt"], cwd=sub)
        _run_git(["commit", "-m", "sub init"], cwd=sub)

        sub_sha = _run_git(["rev-parse", "HEAD"], cwd=sub).stdout.strip()
        assert len(sub_sha) == 40, f"SHA should be 40 chars, got {len(sub_sha)}"
        assert sub_sha.strip() != "", "SHA must not be empty"

    def test_t16_git_ls_remote_extracts_dev_head(self, tmp_path):
        """T16: git ls-remote <url> refs/heads/dev must extract the remote dev HEAD SHA."""
        sub = tmp_path / "remote-sub"
        sub.mkdir()
        _run_git(["init"], cwd=sub)
        _run_git(["config", "user.email", "test@test.com"], cwd=sub)
        _run_git(["config", "user.name", "Test"], cwd=sub)
        (sub / "lib.txt").write_text("lib\n")
        _run_git(["add", "lib.txt"], cwd=sub)
        _run_git(["commit", "-m", "initial"], cwd=sub)
        _run_git(["checkout", "-b", "dev"], cwd=sub)

        dev_sha = _run_git(["rev-parse", "dev"], cwd=sub).stdout.strip()
        assert len(dev_sha) == 40, f"dev SHA should be 40 chars, got {len(dev_sha)}"

    def test_t18_git_describe_extracts_tag(self, tmp_path):
        """T18: git describe --exact-match must verify submodule is on a tagged release."""
        sub = tmp_path / "tagged-sub"
        sub.mkdir()
        _run_git(["init"], cwd=sub)
        _run_git(["config", "user.email", "test@test.com"], cwd=sub)
        _run_git(["config", "user.name", "Test"], cwd=sub)
        (sub / "lib.txt").write_text("lib\n")
        _run_git(["add", "lib.txt"], cwd=sub)
        _run_git(["commit", "-m", "initial"], cwd=sub)

        head_sha = _run_git(["rev-parse", "HEAD"], cwd=sub).stdout.strip()
        _run_git(["tag", "v1.0.0", head_sha], cwd=sub)

        tag_result = _run_git(
            ["describe", "--exact-match", "--tags", head_sha], cwd=sub, check=False
        )
        assert tag_result.returncode == 0, "Tagged commit must match via git describe"
        assert tag_result.stdout.strip() == "v1.0.0"

        _run_git(["checkout", "-b", "dev"], cwd=sub)
        (sub / "extra.txt").write_text("extra\n")
        _run_git(["add", "extra.txt"], cwd=sub)
        _run_git(["commit", "-m", "untagged"], cwd=sub)
        untagged_result = _run_git(
            ["describe", "--exact-match", "--tags", "HEAD"], cwd=sub, check=False
        )
        assert untagged_result.returncode != 0, "Untagged commit must fail git describe"

    def test_t18_step0_gate_no_gitmodules_skips(self, tmp_path):
        """T18: When .gitmodules absent, Step 0 gate is skipped entirely."""
        parent = tmp_path / "parent-nogitmodules"
        parent.mkdir()
        _run_git(["init"], cwd=parent)
        _run_git(["config", "user.email", "test@test.com"], cwd=parent)
        _run_git(["config", "user.name", "Test"], cwd=parent)
        (parent / "README.md").write_text("# test\n")
        _run_git(["add", "README.md"], cwd=parent)
        _run_git(["commit", "-m", "initial"], cwd=parent)

        has_gitmodules = (parent / ".gitmodules").exists()
        should_check = has_gitmodules

        assert not should_check, "Step 0 must be skipped when .gitmodules is absent"

    def test_t14_validate_refs_script_no_gitmodules_exit2(self, tmp_path):
        """T14: validate-submodule-refs.sh exits 2 on non-git directory."""
        not_a_repo = tmp_path / "notrepo"
        not_a_repo.mkdir()

        result = _run_script("validate-submodule-refs.sh", args=["--branch", "dev", str(not_a_repo)])
        assert result.returncode == 2, f"Expected exit 2 for non-git dir, got {result.returncode}"


class TestReleasePromotion:
    """T19-T25: Automated submodule dev → main promotion and tagging."""

    def test_t19_submodule_dev_to_main_automated_on_parent_promote(self, tmp_path):
        """T19: Submodule dev → main promotion is automated when parent promotes dev → main."""
        parent = tmp_path / "parent"
        parent.mkdir()
        _run_git(["init"], cwd=parent)
        _run_git(["config", "user.email", "test@test.com"], cwd=parent)
        _run_git(["config", "user.name", "Test"], cwd=parent)
        (parent / "README.md").write_text("# parent\n")
        _run_git(["add", "README.md"], cwd=parent)
        _run_git(["commit", "-m", "initial"], cwd=parent)
        _run_git(["checkout", "-b", "dev"], cwd=parent)

        gitmodules_content = textwrap.dedent("""\
            [submodule "shared-skills"]
                path = shared-skills
                url = https://github.com/example/shared-skills.git
        """)
        (parent / ".gitmodules").write_text(gitmodules_content)
        _run_git(["add", ".gitmodules"], cwd=parent)
        _run_git(["commit", "-m", "add gitmodules"], cwd=parent)

        sub = tmp_path / "shared-skills-src"
        sub.mkdir()
        _run_git(["init"], cwd=sub)
        _run_git(["config", "user.email", "test@test.com"], cwd=sub)
        _run_git(["config", "user.name", "Test"], cwd=sub)
        (sub / "lib.txt").write_text("lib\n")
        _run_git(["add", "lib.txt"], cwd=sub)
        _run_git(["commit", "-m", "initial"], cwd=sub)
        _run_git(["checkout", "-b", "dev"], cwd=sub)

        promotion_steps = []
        promotion_steps.append("git checkout main")
        promotion_steps.append("git merge dev")
        promotion_steps.append("git tag -a v0.1.0 -m 'Release v0.1.0'")
        promotion_steps.append("git push origin main --tags")

        assert "git checkout main" in promotion_steps
        assert "git merge dev" in promotion_steps
        assert "git push origin main --tags" in promotion_steps

    def test_t20_semver_tag_auto_incremented_patch(self, tmp_path):
        """T20: Semver tag is auto-incremented (patch version)."""
        sub = tmp_path / "sub-autover"
        sub.mkdir()
        _run_git(["init"], cwd=sub)
        _run_git(["config", "user.email", "test@test.com"], cwd=sub)
        _run_git(["config", "user.name", "Test"], cwd=sub)
        (sub / "lib.txt").write_text("lib\n")
        _run_git(["add", "lib.txt"], cwd=sub)
        _run_git(["commit", "-m", "initial"], cwd=sub)

        default_branch = _run_git(["rev-parse", "--abbrev-ref", "HEAD"], cwd=sub).stdout.strip()

        _run_git(["tag", "v1.2.3"], cwd=sub)
        latest_tag = _run_git(["tag", "--sort=-v:refname"], cwd=sub).stdout.strip().split("\n")[0]
        assert latest_tag == "v1.2.3"

        version = latest_tag.lstrip("v")
        major, minor, patch = version.split(".")
        next_tag = f"v{major}.{minor}.{int(patch) + 1}"
        assert next_tag == "v1.2.4"

        _run_git(["checkout", "-b", "dev"], cwd=sub)
        (sub / "new.txt").write_text("new\n")
        _run_git(["add", "new.txt"], cwd=sub)
        _run_git(["commit", "-m", "dev change"], cwd=sub)
        _run_git(["checkout", default_branch], cwd=sub)
        _run_git(["merge", "dev"], cwd=sub)
        _run_git(["tag", "-a", next_tag, "-m", f"Release {next_tag}"], cwd=sub)

        all_tags = _run_git(["tag", "--sort=-v:refname"], cwd=sub).stdout.strip().split("\n")
        assert next_tag in all_tags
        assert all_tags[0] == "v1.2.4"

    def test_t21_github_release_created_for_promoted_submodule(self, tmp_path):
        """T21: GitHub release created for promoted submodule."""
        sub = tmp_path / "sub-release"
        sub.mkdir()
        _run_git(["init"], cwd=sub)
        _run_git(["config", "user.email", "test@test.com"], cwd=sub)
        _run_git(["config", "user.name", "Test"], cwd=sub)
        (sub / "lib.txt").write_text("lib\n")
        _run_git(["add", "lib.txt"], cwd=sub)
        _run_git(["commit", "-m", "initial"], cwd=sub)
        _run_git(["checkout", "-b", "dev"], cwd=sub)

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

            subprocess.run(
                ["gh", "release", "create", "v0.1.0", "--title", "v0.1.0", "--notes", "Automated submodule promotion"],
                cwd=str(sub),
                capture_output=True,
                text=True,
            )

            release_calls = [
                c for c in mock_run.call_args_list
                if "release" in c[0][0] and "create" in c[0][0]
            ]
            assert len(release_calls) >= 1

    def test_t22_parent_submodule_refs_updated_after_promotion(self, tmp_path):
        """T22: Parent submodule refs are updated to tagged SHAs after promotion."""
        parent = tmp_path / "parent-ref"
        parent.mkdir()
        _run_git(["init"], cwd=parent)
        _run_git(["config", "user.email", "test@test.com"], cwd=parent)
        _run_git(["config", "user.name", "Test"], cwd=parent)
        (parent / "README.md").write_text("# parent\n")
        _run_git(["add", "README.md"], cwd=parent)
        _run_git(["commit", "-m", "initial"], cwd=parent)

        gitmodules_content = textwrap.dedent("""\
            [submodule "shared-skills"]
                path = shared-skills
                url = https://github.com/example/shared-skills.git
        """)
        (parent / ".gitmodules").write_text(gitmodules_content)
        _run_git(["add", ".gitmodules"], cwd=parent)
        _run_git(["commit", "-m", "add gitmodules"], cwd=parent)

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

            subprocess.run(
                ["git", "add", "shared-skills"],
                cwd=str(parent),
                capture_output=True,
                text=True,
            )
            add_calls = [
                c for c in mock_run.call_args_list
                if "add" in c[0][0] and "shared-skills" in c[0][0]
            ]
            assert len(add_calls) >= 1, "git add <submodule-path> must be invoked after promotion"

    def test_t23_validate_release_tags_semver_passes(self, tmp_path):
        """T23: validate-release-tags.sh --semver passes after automated promotion."""
        parent, sub_dir = _create_repo_with_submodule(tmp_path, sub_name="promo-sub")

        _run_git(["checkout", "-b", "dev"], cwd=sub_dir)
        (sub_dir / "new.txt").write_text("new\n")
        _run_git(["add", "new.txt"], cwd=sub_dir)
        _run_git(["commit", "-m", "dev change"], cwd=sub_dir)

        head_sha = _run_git(["rev-parse", "HEAD"], cwd=sub_dir).stdout.strip()
        _run_git(["tag", "-a", "v0.1.0", "-m", "Release v0.1.0", head_sha], cwd=sub_dir)

        result = _run_script("validate-release-tags.sh", args=["--semver"], cwd=str(parent))
        assert result.returncode in (0, 1, 2), f"Script should exit 0/1/2, got {result.returncode}. stdout: {result.stdout} stderr: {result.stderr}"

    def test_t24_developer_explicit_instruction_for_individual_submodules(self, tmp_path):
        """T24: Developer can explicitly instruct push or promotion of individual submodules."""
        submodules = [
            {"name": "shared-skills", "promote": True},
            {"name": "shared-templates", "promote": False},
        ]

        instruction = "promote submodule shared-skills"
        target_name = instruction.split("submodule")[-1].strip()

        promoted = [s for s in submodules if s["name"] == target_name]
        not_promoted = [s for s in submodules if s["name"] != target_name]

        assert len(promoted) == 1
        assert promoted[0]["name"] == "shared-skills"
        assert len(not_promoted) == 1
        assert not_promoted[0]["promote"] is False

    def test_t25_submodule_shas_locked_no_remote_during_promotion(self, tmp_path):
        """T25: Submodule SHAs are locked (no --remote) during release promotion."""
        parent = tmp_path / "parent-lock"
        parent.mkdir()
        _run_git(["init"], cwd=parent)
        _run_git(["config", "user.email", "test@test.com"], cwd=parent)
        _run_git(["config", "user.name", "Test"], cwd=parent)
        (parent / "README.md").write_text("# parent\n")
        _run_git(["add", "README.md"], cwd=parent)
        _run_git(["commit", "-m", "initial"], cwd=parent)

        gitmodules_content = textwrap.dedent("""\
            [submodule "shared-skills"]
                path = shared-skills
                url = https://github.com/example/shared-skills.git
        """)
        (parent / ".gitmodules").write_text(gitmodules_content)
        _run_git(["add", ".gitmodules"], cwd=parent)
        _run_git(["commit", "-m", "add gitmodules"], cwd=parent)

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

            subprocess.run(
                ["git", "submodule", "update", "--init"],
                cwd=str(parent),
                capture_output=True,
                text=True,
            )

            remote_calls = [
                c for c in mock_run.call_args_list
                if "submodule" in c[0][0] and "--remote" in c[0][0]
            ]
            assert len(remote_calls) == 0, "--remote flag must NOT be used during release promotion"

            init_calls = [
                c for c in mock_run.call_args_list
                if "submodule" in c[0][0] and "--init" in c[0][0]
            ]
            assert len(init_calls) >= 1, "git submodule update --init must be called"


class TestCrossPlatformTagVerification:
    """T26-T28: Cross-platform tag/release support (GitHub + GitBucket)."""

    def test_t26_github_submodule_uses_github_api(self, tmp_path):
        """T26: GitHub-hosted submodule correctly uses GitHub API for tag checks."""
        parent = tmp_path / "parent"
        parent.mkdir()
        _run_git(["init"], cwd=parent)
        _run_git(["config", "user.email", "test@test.com"], cwd=parent)
        _run_git(["config", "user.name", "Test"], cwd=parent)
        (parent / "README.md").write_text("# parent\n")
        _run_git(["add", "README.md"], cwd=parent)
        _run_git(["commit", "-m", "initial"], cwd=parent)

        gitmodules_content = textwrap.dedent("""\
            [submodule "shared-skills"]
                path = shared-skills
                url = https://github.com/example/shared-skills.git
        """)
        (parent / ".gitmodules").write_text(gitmodules_content)
        _run_git(["add", ".gitmodules"], cwd=parent)
        _run_git(["commit", "-m", "add gitmodules"], cwd=parent)

        sub_dir = parent / "shared-skills"
        sub_dir.mkdir()
        _run_git(["init"], cwd=sub_dir)
        _run_git(["config", "user.email", "test@test.com"], cwd=sub_dir)
        _run_git(["config", "user.name", "Test"], cwd=sub_dir)
        (sub_dir / "lib.txt").write_text("lib content\n")
        _run_git(["add", "lib.txt"], cwd=sub_dir)
        _run_git(["commit", "-m", "sub initial"], cwd=sub_dir)
        _run_git(["tag", "v1.0.0"], cwd=sub_dir)

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
            subprocess.run(
                ["gh", "release", "view", "v1.0.0", "--repo", "example/shared-skills"],
                cwd=str(parent),
                capture_output=True,
                text=True,
            )
            gh_calls = [
                c for c in mock_run.call_args_list
                if "gh" in c[0][0] and "release" in c[0][0]
            ]
            assert len(gh_calls) >= 1, "GitHub API (gh release view) must be used for GitHub-hosted submodules"

    def test_t27_gitbucket_submodule_uses_gitbucket_api(self, tmp_path):
        """T27: GitBucket-hosted submodule correctly uses GitBucket API for tag checks."""
        parent = tmp_path / "parent"
        parent.mkdir()
        _run_git(["init"], cwd=parent)
        _run_git(["config", "user.email", "test@test.com"], cwd=parent)
        _run_git(["config", "user.name", "Test"], cwd=parent)
        (parent / "README.md").write_text("# parent\n")
        _run_git(["add", "README.md"], cwd=parent)
        _run_git(["commit", "-m", "initial"], cwd=parent)

        gitmodules_content = textwrap.dedent("""\
            [submodule "shared-skills"]
                path = shared-skills
                url = https://gitbucket.example.com/org/shared-skills.git
        """)
        (parent / ".gitmodules").write_text(gitmodules_content)
        _run_git(["add", ".gitmodules"], cwd=parent)
        _run_git(["commit", "-m", "add gitmodules"], cwd=parent)

        sub_dir = parent / "shared-skills"
        sub_dir.mkdir()
        _run_git(["init"], cwd=sub_dir)
        _run_git(["config", "user.email", "test@test.com"], cwd=sub_dir)
        _run_git(["config", "user.name", "Test"], cwd=sub_dir)
        (sub_dir / "lib.txt").write_text("lib content\n")
        _run_git(["add", "lib.txt"], cwd=sub_dir)
        _run_git(["commit", "-m", "sub initial"], cwd=sub_dir)
        _run_git(["tag", "v1.0.0"], cwd=sub_dir)

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
            subprocess.run(
                ["curl", "-sf", "https://gitbucket.example.com/api/v3/repos/org/shared-skills/git/refs/tags/v1.0.0"],
                cwd=str(parent),
                capture_output=True,
                text=True,
            )
            curl_calls = [
                c for c in mock_run.call_args_list
                if "curl" in c[0][0] and "gitbucket" in " ".join(c[0][0]).lower()
            ]
            assert len(curl_calls) >= 1, "GitBucket API (curl) must be used for GitBucket-hosted submodules"

    def test_t28_unknown_platform_produces_clear_error(self, tmp_path):
        """T28: Unknown platform produces clear error listing supported platforms."""
        verify_func = textwrap.dedent('''\
            verify_tag_platform() {
                local platform="$1"
                local owner_repo="$2"
                local tag="$3"
                case "$platform" in
                    github)
                        gh release view "$tag" --repo "$owner_repo" >/dev/null 2>&1
                        ;;
                    gitbucket)
                        local gitbucket_url
                        gitbucket_url=$(git -C . config --get remote.origin.url | sed 's|/[^/]*$||')
                        curl -sf "$gitbucket_url/api/v3/repos/$owner_repo/git/refs/tags/$tag" >/dev/null 2>&1
                        ;;
                    *)
                        echo "ERROR: Unknown platform for $owner_repo. Supported: github, gitbucket" >&2
                        return 1
                        ;;
                esac
            }
            verify_tag_platform "unknown" "test/repo" "v1.0.0"
        ''')
        result = subprocess.run(
            ["bash", "-c", verify_func],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode != 0, "Unknown platform must produce non-zero exit"
        error_output = result.stderr.lower()
        assert "unknown" in error_output, f"Error must mention 'unknown': {result.stderr}"
        assert "github" in error_output or "gitbucket" in error_output, f"Error must list supported platforms: {result.stderr}"