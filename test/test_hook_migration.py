import os
from pathlib import Path


class TestHooksDirectory:
    def test_opencode_hooks_dir_exists(self):
        hooks_dir = Path(__file__).resolve().parent.parent / ".opencode" / "hooks"
        assert hooks_dir.is_dir(), ".opencode/hooks/ directory must exist"

    def test_pre_commit_hook_exists(self):
        hook_path = Path(__file__).resolve().parent.parent / ".opencode" / "hooks" / "pre-commit"
        assert hook_path.is_file(), "pre-commit hook must exist in .opencode/hooks/"

    def test_post_commit_hook_exists(self):
        hook_path = Path(__file__).resolve().parent.parent / ".opencode" / "hooks" / "post-commit"
        assert hook_path.is_file(), "post-commit hook must exist in .opencode/hooks/"

    def test_pre_push_hook_exists(self):
        hook_path = Path(__file__).resolve().parent.parent / ".opencode" / "hooks" / "pre-push"
        assert hook_path.is_file(), "pre-push hook must exist in .opencode/hooks/"

    def test_pre_commit_hook_is_executable(self):
        hook_path = Path(__file__).resolve().parent.parent / ".opencode" / "hooks" / "pre-commit"
        if hook_path.is_file():
            assert os.access(hook_path, os.X_OK), "pre-commit hook must be executable"

    def test_pre_push_hook_is_executable(self):
        hook_path = Path(__file__).resolve().parent.parent / ".opencode" / "hooks" / "pre-push"
        if hook_path.is_file():
            assert os.access(hook_path, os.X_OK), "pre-push hook must be executable"


class TestInstallHooksScript:
    def test_install_hooks_script_exists(self):
        script_path = Path(__file__).resolve().parent.parent / "scripts" / "install-hooks.sh"
        assert script_path.is_file(), "scripts/install-hooks.sh must exist"

    def test_install_hooks_script_is_executable(self):
        script_path = Path(__file__).resolve().parent.parent / "scripts" / "install-hooks.sh"
        if script_path.is_file():
            assert os.access(script_path, os.X_OK), "install-hooks.sh must be executable"

    def test_install_hooks_uses_hooks_dir_not_githooks(self):
        script_path = Path(__file__).resolve().parent.parent / "scripts" / "install-hooks.sh"
        content = script_path.read_text()
        assert ".opencode/hooks" in content
        has_removal = "Remove" in content or "remove" in content.lower() or "unset" in content.lower()
        if "core.hooksPath" in content:
            assert has_removal, "Must remove core.hooksPath, not configure it"

    def test_install_hooks_copies_to_git_hooks(self):
        script_path = Path(__file__).resolve().parent.parent / "scripts" / "install-hooks.sh"
        content = script_path.read_text()
        assert ".git/hooks" in content or "DEST_DIR" in content, "install-hooks.sh must copy hooks to .git/hooks/"


class TestGitHooksConfig:
    def test_core_hooks_path_not_set(self):
        result = os.popen("git config core.hooksPath 2>/dev/null").read().strip()
        assert result == "", "core.hooksPath must not be set (hooks installed to .git/hooks/ directly)"

    def test_git_hooks_pre_commit_installed(self):
        import subprocess

        result = subprocess.run(
            ["git", "rev-parse", "--git-common-dir"],
            capture_output=True,
            text=True,
            check=False,
        )
        common_dir = result.stdout.strip()
        hook_path = Path(common_dir) / "hooks" / "pre-commit"
        assert hook_path.is_file(), f"pre-commit hook must be installed at {hook_path}"

    def test_git_hooks_pre_push_installed(self):
        import subprocess

        result = subprocess.run(
            ["git", "rev-parse", "--git-common-dir"],
            capture_output=True,
            text=True,
            check=False,
        )
        common_dir = result.stdout.strip()
        hook_path = Path(common_dir) / "hooks" / "pre-push"
        assert hook_path.is_file(), f"pre-push hook must be installed at {hook_path}"


class TestSemaphoreFile:
    def test_opencode_issue_probe_in_gitignore(self):
        gitignore_path = Path(__file__).resolve().parent.parent / ".gitignore"
        content = gitignore_path.read_text()
        assert ".opencode-issue-probe" in content, ".opencode-issue-probe must be in .gitignore"
