#!/usr/bin/env python3
"""Session initialization script for AI agents.

Extracts git context needed for agent startup:
- DEV_NAME: Developer's git config name (for commit trailers)
- DEV_EMAIL: Developer's git config email (for commit trailers)
- GIT_OWNER: Repository owner (for GitHub/GitBucket API calls)
- GIT_REPO: Repository name (for GitHub/GitBucket API calls)
- GIT_HOOKS_PATH: Git hooks path (to verify hooks installed)
- GIT_REMOTE_URL: Full remote URL (for reference)
- GITHUB_HTML_URL: GitHub web UI base URL (for GitHub remotes)
- GITBUCKET_HTML_URL: GitBucket web UI base URL (from .env, NEVER fabricated)
- GITBUCKET_SSH_URL: GitBucket SSH base URL (host+port, no path, for SSH remotes)
- GITBUCKET_HAS_CREDENTIALS: Whether .env has token configured
- SRCLEIGHT_STATUS: Srclight index health (ok/empty/not_indexed)

Usage:
    uv run python .opencode/scripts/session_init.py

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

    # SSH format: ssh://git@hostname:port/owner/repo.git
    ssh_url_pattern = r"^ssh://git@([^:/]+):(\d+)/([^/]+)/([^/]+?)(?:\.git)?$"
    match = re.match(ssh_url_pattern, url)
    if match:
        owner = match.group(3)
        repo = match.group(4)

    if not owner:
        # SSH format: git@hostname:owner/repo.git (no port, colon separator)
        ssh_short_pattern = r"^git@([^:]+):([^/]+)/([^/]+?)(?:\.git)?$"
        match = re.match(ssh_short_pattern, url)
        if match:
            owner = match.group(2)
            repo = match.group(3)

    if not owner:
        # HTTPS format: https://hostname/owner/repo.git
        https_pattern = r"^https://([^/]+)/([^/]+)/([^/]+?)(?:\.git)?$"
        match = re.match(https_pattern, url)
        if match:
            owner = match.group(2)
            repo = match.group(3)

    if not owner or not repo:
        return None, None, None

    # Read base URL from .env ONLY — never construct from remote hostname
    base_url = _read_gitbucket_url_from_env()

    return base_url, owner, repo


def _read_gitbucket_url_from_env() -> str | None:
    """Read GITBUCKET_HTML_URL (preferred) or GITBUCKET_URL (legacy) from .env file.

    Returns None if neither found.
    """
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

    Returns None if the URL is not an SSH format remote.
    """
    ssh_url_pattern = r"^(ssh://git@[^:/]+:\d+)"
    match = re.match(ssh_url_pattern, url)
    if match:
        return match.group(1)
    return None


def get_remote_url() -> str | None:
    """Get origin remote URL or None if not configured."""
    return run_git_command(["remote", "get-url", "origin"])


def check_srclight() -> None:
    """Check srclight index health via filesystem probe.

    Fast check: looks for the srclight DB file instead of running
    uvx srclight status (which takes ~30 seconds).

    Outputs SRCLEIGHT_STATUS=<status> line.
    Reports warnings to stderr if index is missing or unhealthy.
    """
    db_path = os.path.join(os.getcwd(), ".srclight", "index.db")
    if os.path.exists(db_path):
        file_size = os.path.getsize(db_path)
        if file_size > 0:
            print("SRCLEIGHT_STATUS=ok")
        else:
            print("SRCLEIGHT_STATUS=empty")
            print(
                "# ⚠️ Srclight index is empty. Instruct the user to immediately run:"
                " uvx srclight index --embed qwen3-embedding",
                file=sys.stderr,
            )
    else:
        print("SRCLEIGHT_STATUS=not_indexed")
        print(
            "# ⚠️ Srclight index not found. Instruct the user to immediately run:"
            " uvx srclight index --embed qwen3-embedding",
            file=sys.stderr,
        )


def main() -> int:
    """Extract and output git context."""
    # Get remote URL first - this is required
    remote_url = get_remote_url()
    if not remote_url:
        print("ERROR: No git remote configured", file=sys.stderr)
        print("Run: git remote add origin <url>", file=sys.stderr)
        return 1

    # Get git config values with fallbacks
    user_name = get_user_name()
    user_email = get_user_email()
    hooks_path = get_hooks_path()

    # Output in the specified format
    print("# Session Init - Git Context")
    print(f"DEV_NAME={user_name}")
    print(f"DEV_EMAIL={user_email}")
    print(f"GIT_HOOKS_PATH={hooks_path}")
    print(f"GIT_REMOTE_URL={remote_url}")

    # Check if GitHub remote
    if is_github_remote(remote_url):
        # Parse owner/repo from remote
        owner, repo = parse_git_remote_url(remote_url)
        if not owner or not repo:
            print("ERROR: Failed to parse owner/repo from remote URL", file=sys.stderr)
            print(f"Remote URL: {remote_url}", file=sys.stderr)
            return 1

        print(f"GIT_OWNER={owner}")
        print(f"GIT_REPO={repo}")
        print("GIT_PLATFORM=github")
        print("GITHUB_HTML_URL=https://github.com/")
        print("")
        print("# ============================")
        print("# GITHUB REPOSITORY DETECTED")
        print("# ============================")
        print("# 📋 Invoke: /skill github-issue-creation before creating issues")
        print("# 📋 See: .opencode/skills/github-issue-creation/SKILL.md")
        check_srclight()
        return 0

    # GitBucket remote detected
    if is_gitbucket_remote(remote_url):
        result = parse_gitbucket_url(remote_url)
        base_url, owner, repo = result
        if not owner or not repo:
            print("WARNING: Failed to parse owner/repo from remote URL", file=sys.stderr)
            print(f"Remote URL: {remote_url}", file=sys.stderr)
            print("GIT_PLATFORM=gitbucket")
            print("GITBUCKET_URL=")
            print("GITBUCKET_HAS_CREDENTIALS=false")
            print("")
            print("# ==============================")
            print("# GITBUCKET REPOSITORY DETECTED")
            print("# ==============================")
            print("# 📋 Invoke: /skill gitbucket-api before using GitBucket Python API")
            print("# 📋 See: .opencode/skills/gitbucket-api/SKILL.md")
            return 0

        if not base_url:
            print(
                "WARNING: GITBUCKET_HTML_URL not found in .env — URL generation unavailable",
                file=sys.stderr,
            )
            print(
                "Add GITBUCKET_HTML_URL=<web-ui-base-url> to .env to enable URL generation",
                file=sys.stderr,
            )

        # Check if credentials exist in .env
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

        print(f"GIT_OWNER={owner}")
        print(f"GIT_REPO={repo}")
        print("GIT_PLATFORM=gitbucket")
        print(f"GITBUCKET_HTML_URL={base_url or ''}")
        ssh_url = extract_ssh_url(remote_url)
        if ssh_url:
            print(f"GITBUCKET_SSH_URL={ssh_url}")
        print(f"GITBUCKET_HAS_CREDENTIALS={'true' if has_credentials else 'false'}")
        print("")
        print("# ============================")
        print("# GITBUCKET REPOSITORY DETECTED")
        print("# ============================")
        print("# 📋 Invoke: /skill gitbucket-api before using GitBucket Python API")
        print("# 📋 GitBucket API has specific authentication patterns and limitations")
        print("# 📋 See: .opencode/skills/gitbucket-api/SKILL.md")
        check_srclight()
        return 0

    # Unknown remote type
    print("WARNING: Unknown remote type", file=sys.stderr)
    print(f"Remote URL: {remote_url}", file=sys.stderr)
    print("GIT_PLATFORM=unknown")
    return 2


if __name__ == "__main__":
    sys.exit(main())
