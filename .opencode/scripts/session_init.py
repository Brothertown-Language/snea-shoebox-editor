#!/usr/bin/env python3
"""Session initialization script for AI agents.

Outputs English prose context for LLM consumption on stdout.
Diagnostic and side-effect output goes to stderr — silent on success.

Guard checks (auto-create missing files/branches/worktree):
- CHANGELOG.md: Create with Keep a Changelog header if missing
- .opencode/CHANGELOG.md: Create with minimal header if missing
- dev branch: Create from origin/dev or main/master if missing
- .worktrees/main/: Bootstrap worktree layout if not set up
- .env gitignore: Warn if .env exists but is not in .gitignore

Usage:
    uv run python .opencode/scripts/session_init.py

Exit codes:
    0: Success
    1: No remote configured or failed to parse owner/repo
    2: Non-GitHub/GitBucket remote detected
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys


def run_git_command(args: list[str]) -> str | None:
    """Run a git command and return output, or None if failed."""
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.SubprocessError, OSError):
        pass
    return None


def get_user_name() -> str:
    """Get git user name or fallback to $USER."""
    name = run_git_command(["config", "user.name"])
    if name:
        return name
    return os.environ.get("USER", "unknown")


def get_user_email() -> str:
    """Get git user email or fallback to $USER@$HOSTNAME."""
    email = run_git_command(["config", "user.email"])
    if email:
        return email
    user = os.environ.get("USER", "unknown")
    hostname = os.environ.get("HOSTNAME", "localhost")
    return f"{user}@{hostname}"


def parse_git_remote_url(url: str) -> tuple[str, str] | tuple[None, None]:
    """Parse owner and repo from GitHub remote URL.

    Supports:
    - SSH: git@github.com:owner/repo.git
    - HTTPS: https://github.com/owner/repo.git

    Returns:
        (owner, repo) on success, (None, None) on failure
    """
    ssh_pattern = r"^git@github\.com:([^/]+)/([^/]+?)(?:\.git)?$"
    match = re.match(ssh_pattern, url)
    if match:
        return match.group(1), match.group(2)

    https_pattern = r"^https://github\.com/([^/]+)/([^/]+?)(?:\.git)?$"
    match = re.match(https_pattern, url)
    if match:
        return match.group(1), match.group(2)

    return None, None


def is_github_remote(url: str) -> bool:
    """Check if remote URL is a GitHub remote."""
    return "github.com" in url


def is_gitbucket_remote(url: str) -> bool:
    """Check if remote URL is a GitBucket remote (non-github.com)."""
    return not is_github_remote(url)


def parse_gitbucket_url(
    url: str,
) -> tuple[str | None, str, str] | tuple[None, None, None]:
    """Parse owner and repo from GitBucket remote URL. Base URL comes from .env ONLY.

    Supports:
    - SSH: ssh://git@hostname:port/owner/repo.git
    - SSH: git@hostname:owner/repo.git (no port)
    - HTTPS: https://hostname/owner/repo.git

    Returns:
        (base_url, owner, repo) on success, (None, None, None) on failure

    CRITICAL: base_url is read from .env GITBUCKET_URL, NEVER constructed from
    the remote URL hostname. The SSH host may differ from the web UI host.
    """
    owner: str | None = None
    repo: str | None = None

    ssh_url_pattern = r"^ssh://git@([^:/]+):(\d+)/([^/]+)/([^/]+?)(?:\.git)?$"
    match = re.match(ssh_url_pattern, url)
    if match:
        owner = match.group(3)
        repo = match.group(4)

    if not owner:
        ssh_short_pattern = r"^git@([^:]+):([^/]+)/([^/]+?)(?:\.git)?$"
        match = re.match(ssh_short_pattern, url)
        if match:
            owner = match.group(2)
            repo = match.group(3)

    if not owner:
        https_pattern = r"^https://([^/]+)/([^/]+)/([^/]+?)(?:\.git)?$"
        match = re.match(https_pattern, url)
        if match:
            owner = match.group(2)
            repo = match.group(3)

    if not owner or not repo:
        return None, None, None

    base_url = _read_gitbucket_url_from_env()

    return base_url, owner, repo


def _read_gitbucket_url_from_env() -> str | None:
    """Read GITBUCKET_HTML_URL (preferred) or GITBUCKET_URL (legacy) from .env file."""
    try:
        env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
        if os.path.exists(env_path):
            html_url = None
            legacy_url = None
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("GITBUCKET_HTML_URL="):
                        html_url = line.split("=", 1)[1].strip()
                    elif line.startswith("GITBUCKET_URL="):
                        legacy_url = line.split("=", 1)[1].strip()
            return html_url or legacy_url
    except OSError:
        pass
    return None


def extract_ssh_url(url: str) -> str | None:
    """Extract SSH base URL (host + port, no path) from a GitBucket SSH remote.

    For ssh://git@tomcat-0002.newsrx.com:29418/org/repo.git
    returns ssh://git@tomcat-0002.newsrx.com:29418
    """
    ssh_url_pattern = r"^(ssh://git@[^:/]+:\d+)"
    match = re.match(ssh_url_pattern, url)
    if match:
        return match.group(1)
    return None


def get_remote_url() -> str | None:
    """Get origin remote URL or None if not configured."""
    return run_git_command(["remote", "get-url", "origin"])


def get_current_branch() -> str | None:
    """Get current git branch name or None if HEAD is detached."""
    return run_git_command(["branch", "--show-current"])


def check_srclight() -> str:
    """Check srclight index health. Returns 'indexed', 'empty', or 'not_indexed'."""
    db_path = os.path.join(os.getcwd(), ".srclight", "index.db")
    if os.path.exists(db_path):
        file_size = os.path.getsize(db_path)
        if file_size > 0:
            return "indexed"
        else:
            print(
                "Srclight index is empty. Run: uvx srclight index --embed qwen3-embedding",
                file=sys.stderr,
            )
            return "empty"
    else:
        print(
            "Srclight index not found. Run: uvx srclight index --embed qwen3-embedding",
            file=sys.stderr,
        )
        return "not_indexed"


def get_submodule_dirs() -> list[str]:
    """Get list of submodule directory paths using git config."""
    result = run_git_command(["config", "--file", ".gitmodules", "--get-regexp", "path"])
    if not result:
        return []

    paths: list[str] = []
    for line in result.splitlines():
        parts = line.strip().split()
        if len(parts) >= 2:
            paths.append(parts[-1])
    return paths


def get_source_hooks_dir() -> str | None:
    """Find the .opencode/hooks/ directory or None if missing."""
    hooks_dir = os.path.join(os.getcwd(), ".opencode", "hooks")
    if os.path.isdir(hooks_dir):
        return hooks_dir
    return None


def get_hooks_path() -> str:
    """Get git hooks path or empty string if not configured."""
    hooks = run_git_command(["config", "core.hooksPath"])
    return hooks or ""


def _hooks_match(src: str, dst: str) -> bool:
    """Check if two hook files have the same content."""
    try:
        return os.path.isfile(dst) and open(src).read() == open(dst).read()
    except OSError:
        return False


def _copy_hook(src: str, dst: str) -> bool:
    """Copy a hook file, making it executable."""
    try:
        shutil.copy2(src, dst)
        os.chmod(dst, 0o755)
        return True
    except OSError:
        return False


def install_hooks() -> None:
    """Install git hooks from .opencode/hooks/. Reports failures to stderr."""
    source_dir = get_source_hooks_dir()
    if not source_dir:
        return

    source_hooks = [
        f for f in os.listdir(source_dir) if os.path.isfile(os.path.join(source_dir, f)) and not f.endswith(".sample")
    ]
    if not source_hooks:
        return

    installed_count = 0
    skipped_count = 0
    failed_count = 0

    parent_hooks_dir = os.path.join(os.getcwd(), ".git", "hooks")
    if os.path.isdir(parent_hooks_dir):
        for hook_name in source_hooks:
            src = os.path.join(source_dir, hook_name)
            dst = os.path.join(parent_hooks_dir, hook_name)
            if _hooks_match(src, dst):
                skipped_count += 1
                continue
            if _copy_hook(src, dst):
                installed_count += 1
            else:
                print(f"Failed to install hook {hook_name} into parent repo", file=sys.stderr)
                failed_count += 1

    submodules = get_submodule_dirs()
    for submod_path in submodules:
        if not os.path.isdir(submod_path):
            continue

        hooks_target = os.path.join(os.getcwd(), ".git", "modules", submod_path, "hooks")

        if not os.path.isdir(hooks_target):
            submod_git_file = os.path.join(os.getcwd(), submod_path, ".git")
            if os.path.isfile(submod_git_file):
                try:
                    with open(submod_git_file) as f:
                        gitdir_ref = f.read().strip()
                    if gitdir_ref.startswith("gitdir: "):
                        resolved = gitdir_ref[8:]
                        if not os.path.isabs(resolved):
                            resolved = os.path.join(os.getcwd(), submod_path, resolved)
                        hooks_target = os.path.join(resolved, "hooks")
                except OSError:
                    pass

        if not os.path.isdir(hooks_target):
            print(f"Could not resolve hooks dir for submodule: {submod_path}", file=sys.stderr)
            failed_count += 1
            continue

        for hook_name in source_hooks:
            src = os.path.join(source_dir, hook_name)
            dst = os.path.join(hooks_target, hook_name)
            if _hooks_match(src, dst):
                skipped_count += 1
                continue
            if _copy_hook(src, dst):
                installed_count += 1
            else:
                print(f"Failed to install hook {hook_name} into {submod_path}", file=sys.stderr)
                failed_count += 1

    if installed_count > 0:
        print(f"Installed {installed_count} hook(s)", file=sys.stderr)
    if failed_count > 0:
        print(f"Failed to install {failed_count} hook(s)", file=sys.stderr)

    if get_hooks_path():
        run_git_command(["config", "--unset", "core.hooksPath"])
        print("Removed legacy core.hooksPath config (hooks now in .git/hooks/)", file=sys.stderr)


def _extract_version_from_pyproject() -> str:
    """Extract version string from pyproject.toml, or return '0.1.0' as fallback."""
    pyproject_path = os.path.join(os.getcwd(), "pyproject.toml")
    if os.path.isfile(pyproject_path):
        try:
            with open(pyproject_path) as f:
                for line in f:
                    stripped = line.strip()
                    if stripped.startswith("version"):
                        parts = stripped.split("=", 1)
                        if len(parts) == 2:
                            return parts[1].strip().strip('"').strip("'")
        except OSError:
            pass
    return "0.1.0"


def _ensure_changelog_md() -> str:
    """Create CHANGELOG.md if missing. Returns 'exists', 'created', or 'failed'."""
    changelog_path = os.path.join(os.getcwd(), "CHANGELOG.md")
    if os.path.isfile(changelog_path):
        return "exists"

    version = _extract_version_from_pyproject()
    content = (
        "# Changelog\n"
        "\n"
        "All notable changes to this project will be documented in this file.\n"
        "\n"
        "The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).\n"
        "\n"
        f"## [{version}] - Unreleased\n"
    )
    try:
        with open(changelog_path, "w") as f:
            f.write(content)
        return "created"
    except OSError as e:
        print(f"Failed to create CHANGELOG.md: {e}", file=sys.stderr)
        return "failed"


def _ensure_opencode_changelog_md() -> str:
    """Create .opencode/CHANGELOG.md if missing. Returns 'exists', 'created', or 'failed'."""
    opencode_dir = os.path.join(os.getcwd(), ".opencode")
    changelog_path = os.path.join(opencode_dir, "CHANGELOG.md")
    if os.path.isfile(changelog_path):
        return "exists"
    version = _extract_version_from_pyproject()
    content = (
        "# OpenCode Changelog\n"
        "\n"
        "All notable changes to the `.opencode/` directory (skills, guidelines, agent configuration) "
        "will be documented in this file.\n"
        "\n"
        "The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).\n"
        "\n"
        f"## [{version}] - Unreleased\n"
    )
    try:
        os.makedirs(opencode_dir, exist_ok=True)
        with open(changelog_path, "w") as f:
            f.write(content)
        return "created"
    except OSError as e:
        print(f"Failed to create .opencode/CHANGELOG.md: {e}", file=sys.stderr)
        return "failed"


def _ensure_dev_branch() -> str:
    """Ensure dev branch exists. Returns 'exists', 'created from main', 'created from master', or 'failed'."""
    if run_git_command(["rev-parse", "--verify", "dev"]):
        return "exists"
    if run_git_command(["rev-parse", "--verify", "origin/dev"]):
        run_git_command(["branch", "dev", "origin/dev"])
        return "created from origin/dev"

    for default_branch in ["main", "master"]:
        if run_git_command(["rev-parse", "--verify", default_branch]):
            run_git_command(["branch", "dev", default_branch])
            return f"created from {default_branch}"

    print("Failed to create dev branch — no main or master branch found", file=sys.stderr)
    return "failed"


def is_worktree_setup() -> bool:
    """Check if .worktrees/main/ exists and is a git worktree."""
    main_wt = os.path.join(os.getcwd(), ".worktrees", "main")
    return os.path.isdir(main_wt) and os.path.isdir(os.path.join(main_wt, ".git"))


def _add_to_gitignore(entry: str) -> bool:
    """Add an entry to .gitignore if not already present."""
    gitignore_path = os.path.join(os.getcwd(), ".gitignore")
    try:
        existing_lines: list[str] = []
        if os.path.isfile(gitignore_path):
            with open(gitignore_path) as f:
                existing_lines = f.read().splitlines()
        if entry in existing_lines:
            return True
        with open(gitignore_path, "a") as f:
            if existing_lines and existing_lines[-1] != "":
                f.write("\n")
            f.write(f"{entry}\n")
        return True
    except OSError:
        return False


def bootstrap_worktree_layout() -> bool:
    """Bootstrap .worktrees/main/ if not set up. Returns True on success, False on failure."""
    if is_worktree_setup():
        return True

    main_wt_path = os.path.join(os.getcwd(), ".worktrees", "main")

    if os.path.isdir(main_wt_path):
        result = run_git_command(["worktree", "remove", main_wt_path, "--force"])
        if result is None:
            print("Failed to remove stale .worktrees/main/ directory", file=sys.stderr)
            return False

    main_branch = "main"
    if run_git_command(["rev-parse", "--verify", "main"]) is None:
        if run_git_command(["rev-parse", "--verify", "master"]) is not None:
            main_branch = "master"
        else:
            print("No main or master branch found — worktree setup requires a default branch", file=sys.stderr)
            return False

    current = get_current_branch()

    if current and current != "dev":
        stash_output = run_git_command(["stash", "push", "-u", "-m", "WIP: before worktree bootstrap"])
        had_stash = stash_output is not None
    else:
        had_stash = False

    if current and current != "dev":
        run_git_command(["checkout", "dev"])

    result = run_git_command(["worktree", "add", main_wt_path, main_branch])
    if result is None:
        print("Failed to create .worktrees/main/ worktree", file=sys.stderr)
        if current and current != "dev":
            run_git_command(["checkout", current])
        return False

    _add_to_gitignore(".worktrees/")

    submod_dirs = get_submodule_dirs()
    if submod_dirs:
        init_result = run_git_command(["submodule", "update", "--init"])
        if init_result is not None:
            for submod in submod_dirs:
                submod_path = os.path.join(main_wt_path, submod)
                if os.path.isdir(submod_path):
                    run_git_command(["-C", main_wt_path, "submodule", "update", "--init", submod])

    if current and current != "dev":
        run_git_command(["checkout", current])
        if had_stash:
            run_git_command(["stash", "pop"])

    return True


def _check_env_gitignored() -> bool:
    """Check if .env exists and is in .gitignore. Returns True if safe (gitignored or doesn't exist)."""
    if not os.path.isfile(os.path.join(os.getcwd(), ".env")):
        return True
    gitignore_path = os.path.join(os.getcwd(), ".gitignore")
    if not os.path.isfile(gitignore_path):
        return False
    try:
        with open(gitignore_path) as f:
            for line in f:
                stripped = line.strip()
                if stripped == ".env" or stripped == "/.env":
                    return True
    except OSError:
        pass
    return False


def run_guard_checks() -> list[str]:
    """Run guard checks silently. Returns list of problem descriptions."""
    problems: list[str] = []
    changelog_status = _ensure_changelog_md()
    if changelog_status == "failed":
        problems.append("CHANGELOG.md: failed to create")
    opencode_changelog_status = _ensure_opencode_changelog_md()
    if opencode_changelog_status == "failed":
        problems.append(".opencode/CHANGELOG.md: failed to create")
    dev_branch_status = _ensure_dev_branch()
    if "failed" in dev_branch_status:
        problems.append(f"dev branch: {dev_branch_status}")
    if not _check_env_gitignored():
        problems.append("WARNING: .env is NOT in .gitignore — secrets may be committed to version control")
    return problems


def main() -> int:
    """Extract and output git context as English prose for LLM consumption."""
    remote_url = get_remote_url()
    if not remote_url:
        print("No git remote configured. Run: git remote add origin <url>", file=sys.stderr)
        return 1

    user_name = get_user_name()
    user_email = get_user_email()

    srclight_status = check_srclight()
    install_hooks()
    guard_problems = run_guard_checks()
    worktree_ok = bootstrap_worktree_layout()

    current_branch = get_current_branch() or "unknown"

    if is_github_remote(remote_url):
        owner, repo = parse_git_remote_url(remote_url)
        if not owner or not repo:
            print("Could not determine repository owner from remote URL.", file=sys.stderr)
            print(f"Remote URL: {remote_url}", file=sys.stderr)
            return 1

        print(f"Repository: {repo} (GitHub)")
        print(f"Owner: {owner}")
        print(f'Use owner="{owner}" and repo="{repo}" for all GitHub tool calls.')
        print("HTML base: https://github.com/")
        print(f"Developer: {user_name} ({user_email})")
        print(f"Current branch: {current_branch}")

        if worktree_ok:
            print("Worktrees: available")
        else:
            print("Worktrees: setup failed — HALT and report to developer before proceeding")

        if srclight_status == "indexed":
            print("Srclight: indexed")
        else:
            print("Srclight: NOT indexed — tell the developer to run: uvx srclight index --embed qwen3-embedding")

        for problem in guard_problems:
            print(problem)

        return 0

    if is_gitbucket_remote(remote_url):
        result = parse_gitbucket_url(remote_url)
        base_url, owner, repo = result
        if not owner or not repo:
            print("Could not determine repository owner from remote URL.", file=sys.stderr)
            print(f"Remote URL: {remote_url}", file=sys.stderr)
            return 1

        if not base_url:
            print("GITBUCKET_HTML_URL not found in .env — URL generation unavailable", file=sys.stderr)

        has_credentials = False
        try:
            env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
            if os.path.exists(env_path):
                with open(env_path) as f:
                    content = f.read()
                    has_credentials = "GITBUCKET_TOKEN=" in content and (
                        "GITBUCKET_HTML_URL=" in content or "GITBUCKET_URL=" in content
                    )
        except OSError:
            pass

        print(f"Repository: {repo} (GitBucket)")
        print(f"Owner: {owner}")
        print(f'Use owner="{owner}" and repo="{repo}" for all GitBucket tool calls.')
        if base_url:
            print(f"HTML base: {base_url}")
        ssh_url = extract_ssh_url(remote_url)
        if ssh_url:
            print(f"SSH base: {ssh_url}")
        print(f"API credentials: {'configured' if has_credentials else 'NOT configured'}")
        print(f"Developer: {user_name} ({user_email})")
        print(f"Current branch: {current_branch}")

        if worktree_ok:
            print("Worktrees: available")
        else:
            print("Worktrees: setup failed — HALT and report to developer before proceeding")

        if srclight_status == "indexed":
            print("Srclight: indexed")
        else:
            print("Srclight: NOT indexed — tell the developer to run: uvx srclight index --embed qwen3-embedding")

        for problem in guard_problems:
            print(problem)

        return 0

    print("Unknown remote type", file=sys.stderr)
    print(f"Remote URL: {remote_url}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
