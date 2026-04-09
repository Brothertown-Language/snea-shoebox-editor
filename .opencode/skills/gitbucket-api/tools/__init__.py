"""
GitBucket API Python Tooling

Provides pure-stdlib Python tooling for GitBucket API operations.
No external dependencies required.

Usage:
    from skills.gitbucket_api.tools import GitBucketAPI

    api = GitBucketAPI()
    issue = api.create_issue(owner="org", repo="project", title="Bug fix")
"""

from pathlib import Path

from .exceptions import (
    GitBucketError,
    AuthenticationError,
    NotFoundError,
    ValidationError,
    RateLimitError,
    ServerError,
)

from .auth import (
    GitBucketAuth,
    _get_credentials,
    _get_config_file,
    _create_config_template,
)

from .gitbucket_api import GitBucketAPI
from .session import get_session_values


def create_config_file() -> Path:
    """Create secrets.toml template at platform-specific location.

    Returns:
        Path to created or existing config file

    Usage:
        from skills.gitbucket_api.tools import create_config_file

        config_path = create_config_file()
        print(f"Config file created at: {config_path}")
        print("Edit the file and add your GitBucket credentials.")
    """
    return _create_config_template()


__all__ = [
    "GitBucketError",
    "AuthenticationError",
    "NotFoundError",
    "ValidationError",
    "RateLimitError",
    "ServerError",
    "GitBucketAuth",
    "GitBucketAPI",
    "get_session_values",
    "create_config_file",
]
