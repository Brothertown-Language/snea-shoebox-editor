#!/usr/bin/env python3
"""Session initialization script for AI agents.

Extracts git context needed for agent startup:
- DEV_NAME: Human collaborator name (for commit trailers)
- DEV_EMAIL: Human collaborator email (for commit trailers)
- GIT_OWNER: Repository owner (for GitHub MCP API calls)
- GIT_REPO: Repository name (for GitHub MCP API calls)
- GIT_HOOKS_PATH: Git hooks path (to verify hooks installed)
- GIT_REMOTE_URL: Full remote URL (for reference)

Usage:
    uv run python ai_bin/session_init.py

Exit codes:
    0: Success
    1: No remote configured
    2: Non-GitHub remote detected
"""

import os
import re
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


def get_hooks_path() -> str:
    """Get git hooks path or empty string if not configured."""
    hooks = run_git_command(["config", "core.hooksPath"])
    return hooks or ""


def parse_git_remote_url(url: str) -> tuple[str, str] | tuple[None, None]:
    """Parse owner and repo from GitHub remote URL.

    Supports:
    - SSH: git@github.com:owner/repo.git
    - HTTPS: https://github.com/owner/repo.git

    Returns:
        (owner, repo) on success, (None, None) on failure
    """
    # SSH format: git@github.com:owner/repo.git
    ssh_pattern = r"^git@github\.com:([^/]+)/([^/]+?)(?:\.git)?$"
    match = re.match(ssh_pattern, url)
    if match:
        return match.group(1), match.group(2)

    # HTTPS format: https://github.com/owner/repo.git
    https_pattern = r"^https://github\.com/([^/]+)/([^/]+?)(?:\.git)?$"
    match = re.match(https_pattern, url)
    if match:
        return match.group(1), match.group(2)

    return None, None


def is_github_remote(url: str) -> bool:
    """Check if remote URL is a GitHub remote."""
    return "github.com" in url


def get_remote_url() -> str | None:
    """Get origin remote URL or None if not configured."""
    return run_git_command(["remote", "get-url", "origin"])


def verify_hooks_installed() -> bool:
    """Check if git hooks are installed. Returns True if installed."""
    hooks_path = get_hooks_path()
    repo_root = run_git_command(["rev-parse", "--show-toplevel"])

    if not repo_root:
        return False

    expected_hooks_dir = ".githooks"
    pre_commit_hook = os.path.join(repo_root, expected_hooks_dir, "pre-commit")

    # Check if hooks path is configured
    if hooks_path != expected_hooks_dir:
        return False

    # Check if pre-commit hook exists and is executable
    if not os.path.isfile(pre_commit_hook):
        return False

    return True


def main() -> int:
    """Extract and output git context."""
    # Get remote URL first - this is required
    remote_url = get_remote_url()
    if not remote_url:
        print("ERROR: No git remote configured", file=sys.stderr)
        print("Run: git remote add origin <url>", file=sys.stderr)
        return 1

    # Check if GitHub remote
    if not is_github_remote(remote_url):
        print("WARNING: Non-GitHub remote detected", file=sys.stderr)
        print(f"Remote URL: {remote_url}", file=sys.stderr)
        print("GitHub MCP operations will not work", file=sys.stderr)
        return 2

    # Parse owner/repo from remote
    owner, repo = parse_git_remote_url(remote_url)
    if not owner or not repo:
        print("ERROR: Failed to parse owner/repo from remote URL", file=sys.stderr)
        print(f"Remote URL: {remote_url}", file=sys.stderr)
        return 1

    # Get git config values with fallbacks
    user_name = get_user_name()
    user_email = get_user_email()
    hooks_path = get_hooks_path()

    # Output in the specified format
    print("# Session Init - Git Context")
    print(f"DEV_NAME={user_name}")
    print(f"DEV_EMAIL={user_email}")
    print(f"GIT_OWNER={owner}")
    print(f"GIT_REPO={repo}")
    print(f"GIT_HOOKS_PATH={hooks_path}")
    print(f"GIT_REMOTE_URL={remote_url}")

    # Verify hooks are installed (warning only, do not halt)
    if not verify_hooks_installed():
        print("", file=sys.stderr)
        print("=" * 70, file=sys.stderr)
        print("WARNING: Git hooks are not installed!", file=sys.stderr)
        print("=" * 70, file=sys.stderr)
        print("", file=sys.stderr)
        print("Branch protection will not be enforced on commit.", file=sys.stderr)
        print("Protected branches: main, dev", file=sys.stderr)
        print("", file=sys.stderr)
        print("AI Agent: Relay this warning to the developer.", file=sys.stderr)
        print("", file=sys.stderr)
        print("To install hooks:", file=sys.stderr)
        print("    ./scripts/install-hooks.sh", file=sys.stderr)
        print("", file=sys.stderr)
        print("Developer: Decide whether to install hooks before proceeding.", file=sys.stderr)
        print("=" * 70, file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
