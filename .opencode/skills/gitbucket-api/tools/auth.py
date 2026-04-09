"""
GitBucket API Authentication

Handles token authentication for GitBucket API.

Authentication methods:
- Token authentication (ONLY working method): Authorization: token {TOKEN}
- Basic authentication (NON-FUNCTIONAL): GitBucket returns "Bad credentials" for
  basic auth against all endpoints. The username/password parameters, GITBUCKET_USERNAME,
  GITBUCKET_PASSWORD environment variables, and .env entries are retained only for
  forward-compatibility in case a future GitBucket version fixes basic auth.

Credential sources (in order of priority):
1. Explicit parameters (token)
2. Environment variables (GITBUCKET_TOKEN)
3. Project .env file (<project>/.env)
4. User config file (platform-specific, see _get_config_file())
"""

import base64
import os
import platform
from pathlib import Path
from typing import Dict, Optional


def _get_config_file() -> Path:
    """Get platform-specific config file path.

    Returns:
        Path to secrets.toml

    Platform locations:
        - Linux: ~/.config/gitbucket/secrets.toml
        - macOS: ~/.config/gitbucket/secrets.toml (or ~/Library/Application Support/gitbucket/secrets.toml)
        - Windows: %APPDATA%/gitbucket/secrets.toml (or %LOCALAPPDATA%/gitbucket/secrets.toml)

    Note:
        Follows XDG Base Directory Specification on Linux/macOS.
        Uses APPDATA on Windows for Roaming profile support.
    """
    system = platform.system()

    if system == "Windows":
        # Windows: Use APPDATA for Roaming profile (synced across machines)
        # Fallback to LOCALAPPDATA if APPDATA not available
        appdata = os.environ.get("APPDATA") or os.environ.get("LOCALAPPDATA")
        if appdata:
            return Path(appdata) / "gitbucket" / "secrets.toml"
        # Fallback to user home
        return Path.home() / "AppData" / "Roaming" / "gitbucket" / "secrets.toml"

    elif system == "Darwin":
        # macOS: Follow XDG spec, but also check ~/Library/Application Support
        xdg_config = os.environ.get("XDG_CONFIG_HOME")
        if xdg_config:
            return Path(xdg_config) / "gitbucket" / "secrets.toml"
        # Default macOS location
        return Path.home() / ".config" / "gitbucket" / "secrets.toml"

    else:
        # Linux and other Unix-like: XDG Base Directory Specification
        xdg_config = os.environ.get("XDG_CONFIG_HOME")
        if xdg_config:
            return Path(xdg_config) / "gitbucket" / "secrets.toml"
        # Default Linux location
        return Path.home() / ".config" / "gitbucket" / "secrets.toml"


def _create_config_template(toml_path: Optional[Path] = None) -> Path:
    """Create secrets.toml with placeholder content if it doesn't exist.

    Args:
        toml_path: Path to TOML file (default: platform-specific location)

    Returns:
        Path to created or existing config file

    Raises:
        OSError: If unable to create directory or file

    Note:
        Creates parent directories as needed.
        Cross-platform: Works on Linux, macOS, and Windows.
    """
    if toml_path is None:
        toml_path = _get_config_file()

    if toml_path.exists():
        return toml_path

    # Create parent directories
    toml_path.parent.mkdir(parents=True, exist_ok=True)

    # Write template content
    template_content = """# GitBucket API Configuration
# This file stores your GitBucket credentials.
# 
# Get your token from: https://<gitbucket-url>/_settings/tokens
# 
# Fill in the values below:

# GitBucket base URL (required)
url = "https://gitbucket.example.com/gitbucket/"

# Personal access token (required for API operations)
token = "your-personal-access-token"

# Username for basic auth (optional, for admin endpoints)
username = ""

# Password for basic auth (optional, for admin endpoints)
password = ""

# Note: Token authentication is preferred for all non-admin operations.
# Basic auth is ONLY required for admin endpoints (/admin/users, /admin/organizations).
"""

    with open(toml_path, "w", encoding="utf-8") as f:
        f.write(template_content)

    return toml_path


def _load_from_env_file(env_path: Optional[Path] = None) -> Dict[str, str]:
    """Load credentials from .env file.

    Args:
        env_path: Path to .env file (default: project root .env)

    Returns:
        Dict with url, token, username, password (short-form keys)

    Note:
        Maps env-var names to short-form keys for compatibility with
        _get_credentials():
        - GITBUCKET_HTML_URL / GITBUCKET_URL -> url
        - GITBUCKET_TOKEN -> token
        - GITBUCKET_USERNAME -> username (NON-FUNCTIONAL: basic auth broken)
        - GITBUCKET_PASSWORD -> password (NON-FUNCTIONAL: basic auth broken)
    """
    if env_path is None:
        # Find project root by looking for .git directory
        current = Path.cwd()
        while current != current.parent:
            if (current / ".git").exists():
                env_path = current / ".env"
                break
            current = current.parent
        else:
            # Fallback: current directory
            env_path = Path.cwd() / ".env"

    if not env_path.exists():
        return {}

    credentials = {}
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip("'\"")
                if key in (
                    "GITBUCKET_HTML_URL",
                    "GITBUCKET_URL",
                    "GITBUCKET_TOKEN",
                    "GITBUCKET_USERNAME",
                    "GITBUCKET_PASSWORD",
                ):
                    credentials[key] = value

    # Map env-var keys to short-form keys (consistent with _load_from_toml_file)
    mapped = {}
    if credentials.get("GITBUCKET_HTML_URL") or credentials.get("GITBUCKET_URL"):
        mapped["url"] = credentials.get("GITBUCKET_HTML_URL") or credentials.get("GITBUCKET_URL")
    if credentials.get("GITBUCKET_TOKEN"):
        mapped["token"] = credentials["GITBUCKET_TOKEN"]
    if credentials.get("GITBUCKET_USERNAME"):
        mapped["username"] = credentials["GITBUCKET_USERNAME"]
    if credentials.get("GITBUCKET_PASSWORD"):
        mapped["password"] = credentials["GITBUCKET_PASSWORD"]

    return mapped


def _load_from_toml_file(
    toml_path: Optional[Path] = None, create_if_missing: bool = False
) -> Dict[str, str]:
    """Load credentials from secrets.toml file.

    Args:
        toml_path: Path to TOML file (default: platform-specific location)
        create_if_missing: Create template file if it doesn't exist

    Returns:
        Dict with url, token, username, password

    Note:
        This does NOT require toml library. Uses simple key=value parsing.
        For full TOML support, install toml package.

        If create_if_missing=True, creates a template file at platform-specific location.
    """
    if toml_path is None:
        toml_path = _get_config_file()

    if not toml_path.exists():
        if create_if_missing:
            _create_config_template(toml_path)
        return {}

    credentials = {}
    with open(toml_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("["):
                continue
            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip("'\"")
                # Map TOML keys to environment variable names
                key_map = {
                    "url": "GITBUCKET_HTML_URL",
                    "token": "GITBUCKET_TOKEN",
                    "username": "GITBUCKET_USERNAME",
                    "password": "GITBUCKET_PASSWORD",
                }
                if key in key_map:
                    credentials[key_map[key]] = value

    return credentials


def _get_credentials(
    token: Optional[str] = None,
    username: Optional[str] = None,
    password: Optional[str] = None,
    url: Optional[str] = None,
    create_config_if_missing: bool = False,
) -> Dict[str, Optional[str]]:
    """Get credentials from all sources in priority order.

    Priority:
    1. Explicit parameters
    2. Environment variables
    3. Project .env file
    4. User config file (platform-specific secrets.toml)

    Args:
        token: Explicit token
        username: Explicit username (NON-FUNCTIONAL: basic auth broken in GitBucket)
        password: Explicit password (NON-FUNCTIONAL: basic auth broken in GitBucket)
        url: Explicit URL
        create_config_if_missing: Create secrets.toml template if missing

    Returns:
        Dict with url, token, username, password
    """
    # Start with environment variables (GITBUCKET_HTML_URL preferred, fallback to GITBUCKET_URL)
    creds = {
        "url": os.environ.get("GITBUCKET_HTML_URL") or os.environ.get("GITBUCKET_URL"),
        "token": os.environ.get("GITBUCKET_TOKEN"),
        "username": os.environ.get("GITBUCKET_USERNAME"),
        "password": os.environ.get("GITBUCKET_PASSWORD"),
    }

    # Override with .env file
    env_file = _load_from_env_file()
    for key in creds:
        if key in env_file and creds.get(key) is None:
            creds[key] = env_file[key]

    # Override with TOML file
    toml_file = _load_from_toml_file(create_if_missing=create_config_if_missing)
    for key in creds:
        if key in toml_file and creds.get(key) is None:
            creds[key] = toml_file[key]

    # Override with explicit parameters (highest priority)
    if url is not None:
        creds["url"] = url
    if token is not None:
        creds["token"] = token
    if username is not None:
        creds["username"] = username
    if password is not None:
        creds["password"] = password

    return creds


class GitBucketAuth:
    """Manages authentication headers for GitBucket API.

    Authentication methods:
    1. Token authentication (ONLY working method): Authorization: token {TOKEN}
    2. Basic authentication (NON-FUNCTIONAL): GitBucket returns "Bad credentials"
       for basic auth. Username/password parameters are retained for forward-
       compatibility only.

    Credential sources (in order of priority):
    1. Explicit parameters (token, url)
    2. Environment variables (GITBUCKET_TOKEN, GITBUCKET_HTML_URL)
    3. Project .env file (<project>/.env)
    4. User config file (~/.config/gitbucket/secrets.toml)

    Usage:
        # From .env or secrets.toml (recommended)
        auth = GitBucketAuth()
        headers = auth.get_headers()

        # Token auth (explicit)
        auth = GitBucketAuth(token="your-token")
        headers = auth.get_headers()
    """

    def __init__(
        self,
        token: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        url: Optional[str] = None,
        create_config_if_missing: bool = False,
    ):
        """Initialize authentication.

        Args:
            token: GitBucket personal access token
            username: Username for basic auth (NON-FUNCTIONAL: basic auth broken)
            password: Password for basic auth (NON-FUNCTIONAL: basic auth broken)
            url: GitBucket base URL
            create_config_if_missing: Create secrets.toml template if missing

        Note:
            Token auth is the ONLY working authentication method.
            Basic auth (username/password) does NOT work — GitBucket returns
            "Bad credentials" for all basic auth requests.

            Credentials are loaded in this priority:
            1. Explicit parameters (token, url)
            2. Environment variables (GITBUCKET_TOKEN, GITBUCKET_HTML_URL)
            3. Project .env file (<project>/.env)
            4. User config file (platform-specific secrets.toml)

            Platform config locations:
            - Linux: ~/.config/gitbucket/secrets.toml
            - macOS: ~/.config/gitbucket/secrets.toml
            - Windows: %APPDATA%/gitbucket/secrets.toml

            If create_config_if_missing=True, creates a template file at the
            platform-specific location if it doesn't exist.
        """
        creds = _get_credentials(
            token=token,
            username=username,
            password=password,
            url=url,
            create_config_if_missing=create_config_if_missing,
        )
        self.url = creds["url"]
        self.token = creds["token"]
        self.username = creds["username"]
        self.password = creds["password"]

    def get_headers(self, use_basic: bool = False) -> Dict[str, str]:
        """Get authentication headers.

        Args:
            use_basic: Use basic auth instead of token (NON-FUNCTIONAL: always fails)

        Returns:
            Dict with Content-Type and Authorization headers

        Raises:
            ValueError: If no token available

        Examples:
            # Token auth (default, ONLY working method)
            >>> auth = GitBucketAuth(token="abc123")
            >>> auth.get_headers()
            {"Content-Type": "application/json", "Authorization": "token abc123"}
        """
        headers = {"Content-Type": "application/json"}

        if use_basic:
            if not self.username or not self.password:
                raise ValueError(
                    "Basic auth requires username and password. "
                    "Set GITBUCKET_USERNAME and GITBUCKET_PASSWORD in .env, "
                    "~/.config/gitbucket/secrets.toml, or environment variables."
                )
            credentials = base64.b64encode(
                f"{self.username}:{self.password}".encode()
            ).decode()
            headers["Authorization"] = f"Basic {credentials}"
        elif self.token:
            headers["Authorization"] = f"token {self.token}"
        else:
            raise ValueError(
                "No authentication available. "
                "Set GITBUCKET_TOKEN in:\n"
                "  - .env file (project root)\n"
                "  - ~/.config/gitbucket/secrets.toml\n"
                "  - environment variable\n"
                "Or provide username/password for basic auth."
            )

        return headers

    def has_token(self) -> bool:
        """Check if token authentication is available.

        Returns:
            True if token is configured
        """
        return bool(self.token)

    def has_basic(self) -> bool:
        """Check if basic authentication is available.

        Returns:
            True if username and password are configured
        """
        return bool(self.username and self.password)

    def __repr__(self) -> str:
        """String representation (safe, no credentials)."""
        methods = []
        if self.token:
            methods.append("token")
        if self.username and self.password:
            methods.append("basic")
        return f"GitBucketAuth(methods={methods})"
