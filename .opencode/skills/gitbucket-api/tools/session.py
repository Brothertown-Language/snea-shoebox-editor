"""
Session Init Integration

Extracts GitBucket credentials from session init script output.
"""

import subprocess


def get_session_values() -> dict[str, str]:
    """Extract values from session init script.

    Runs `uv run .opencode/tools/session-init` and parses output.

    Returns:
        Dict with GITBUCKET_URL, GITBUCKET_TOKEN, GIT_OWNER, GIT_REPO, etc.

    Example:
        >>> values = get_session_values()
        >>> values['GITBUCKET_URL']
        'https://gitbucket.example.com/gitbucket/'
        >>> values['GIT_OWNER']
        'myorg'
        >>> values['GIT_REPO']
        'myrepo'

    Raises:
        subprocess.CalledProcessError: Session init script failed
        ValueError: Expected variable not found in output
    """
    result = subprocess.run(
        ["uv", "run", ".opencode/tools/session-init"],
        capture_output=True,
        text=True,
        check=True,
    )

    values = {}
    for line in result.stdout.strip().split("\n"):
        if "=" in line:
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip()

    return values


def get_gitbucket_url() -> str:
    """Get GitBucket HTML URL from session init.

    Returns:
        GitBucket HTML base URL (from GITBUCKET_HTML_URL, with fallback to GITBUCKET_URL)

    Raises:
        ValueError: Neither GITBUCKET_HTML_URL nor GITBUCKET_URL found
    """
    values = get_session_values()
    url = values.get("GITBUCKET_HTML_URL") or values.get("GITBUCKET_URL")
    if not url:
        raise ValueError("Neither GITBUCKET_HTML_URL nor GITBUCKET_URL found in session init output")
    return url


def get_gitbucket_token() -> str:
    """Get GitBucket token from session init.

    Returns:
        GitBucket personal access token

    Raises:
        ValueError: GITBUCKET_TOKEN not found in environment
    """
    import os

    token = os.environ.get("GITBUCKET_TOKEN")
    if not token:
        raise ValueError("GITBUCKET_TOKEN not found in environment. Add GITBUCKET_TOKEN=your-token to .env file")
    return token


def is_gitbucket() -> bool:
    """Check if current repo is GitBucket (not GitHub).

    Returns:
        True if GIT_PLATFORM=gitbucket
    """
    values = get_session_values()
    return values.get("GIT_PLATFORM") == "gitbucket"


def is_github() -> bool:
    """Check if current repo is GitHub.

    Returns:
        True if GIT_PLATFORM=github
    """
    values = get_session_values()
    return values.get("GIT_PLATFORM") == "github"


def get_repo_context() -> dict[str, str]:
    """Get repository context from session init.

    Returns:
        Dict with GIT_OWNER, GIT_REPO, GIT_PLATFORM

    Example:
        >>> context = get_repo_context()
        >>> print(f"{context['GIT_OWNER']}/{context['GIT_REPO']}")
        'myorg/myrepo'
    """
    values = get_session_values()
    required = ["GIT_OWNER", "GIT_REPO", "GIT_PLATFORM"]
    missing = [k for k in required if k not in values]
    if missing:
        raise ValueError(f"Missing required values: {', '.join(missing)}")
    return {k: values[k] for k in required}
