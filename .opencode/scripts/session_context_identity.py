#!/usr/bin/env -S uv run --script
# /// script
# requires-python = "~=3.12"
# dependencies = []
# ///
"""Identity section emitter for AI agent session context.

Extracted from session_context.py per spec #1107 (R6: intentional
deduplication of shared helpers across split scripts).

Emits ONLY the Repository Identity section — no trigger warnings, no
"Respond to the above" directive. Called by session-enforcement.ts at
system.transform time.

Exit codes:
    0: Success
    1: No git remote or identity resolution failure
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path


def run_git(args: list[str]) -> str | None:
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


def get_remote_url() -> str | None:
    return run_git(["remote", "get-url", "origin"])


def get_root_dir() -> str | None:
    return run_git(["rev-parse", "--show-toplevel"])


def detect_platform(remote_url: str) -> str:
    if "github.com" in remote_url:
        return "github"
    if "gitbucket" in remote_url.lower() or (
        not remote_url.startswith("git@github.com") and not remote_url.startswith("https://github.com")
    ):
        try:
            result = subprocess.run(
                ["git", "ls-remote", "--heads", remote_url],
                capture_output=True,
                text=True,
                check=False,
                timeout=3,
            )
            if result.returncode == 0:
                return "gitbucket"
        except (subprocess.SubprocessError, OSError):
            pass
    return "unknown"


def parse_owner_repo(remote_url: str, platform: str) -> tuple[str | None, str | None]:
    if platform == "github":
        for pattern in [
            r"^git@github\.com:([^/]+)/([^/]+?)(?:\.git)?$",
            r"^https://github\.com/([^/]+)/([^/]+?)(?:\.git)?$",
        ]:
            m = re.match(pattern, remote_url)
            if m:
                return m.group(1), m.group(2)
    else:
        for pattern in [
            r"^ssh://git@[^:/]+:\d+/([^/]+)/([^/]+?)(?:\.git)?$",
            r"^git@[^:]+:([^/]+)/([^/]+?)(?:\.git)?$",
            r"^https://[^/]+/([^/]+)/([^/]+?)(?:\.git)?$",
        ]:
            m = re.match(pattern, remote_url)
            if m:
                return m.group(1), m.group(2)
    return None, None


def probe_credentials_tier1(platform: str, root_dir: str) -> str:
    env_path = Path(root_dir) / ".env"
    secrets_path = Path(root_dir) / ".streamlit" / "secrets.toml"

    github_token_keys = ["GITHUB_TOKEN", "GH_TOKEN", "GITHUB_PERSONAL_ACCESS_TOKEN"]
    gitbucket_token_keys = ["GITBUCKET_TOKEN"]

    token_keys = github_token_keys if platform == "github" else gitbucket_token_keys

    for _source_label, source_path, parser in [
        (".env", env_path, _parse_env_token),
        ("secrets.toml", secrets_path, _parse_secrets_toml_token),
        ("environment", None, _parse_env_var_token),
    ]:
        token_value = parser(source_path, token_keys) if source_path else _parse_env_var_token(None, token_keys)
        if token_value:
            return "present"

    return "missing"


def _parse_env_token(env_path: Path, keys: list[str]) -> str | None:
    if not env_path.is_file():
        return None
    try:
        content = env_path.read_text()
        for line in content.splitlines():
            stripped = line.strip()
            for key in keys:
                if stripped.startswith(f"{key}="):
                    value = stripped.split("=", 1)[1].strip().strip("'\"")
                    if value:
                        return value
    except OSError:
        pass
    return None


def _parse_secrets_toml_token(secrets_path: Path, keys: list[str]) -> str | None:
    if not secrets_path.is_file():
        return None
    try:
        content = secrets_path.read_text()
        toml_keys = [k.lower().replace("_", "") for k in keys]
        for line in content.splitlines():
            stripped = line.strip()
            for _key, toml_key in zip(keys, toml_keys, strict=False):
                if stripped.startswith(f"{toml_key} =") or stripped.startswith(f"{toml_key}="):
                    value = stripped.split("=", 1)[1].strip().strip("'\"")
                    if value:
                        return value
    except OSError:
        pass
    return None


def _parse_env_var_token(_: None, keys: list[str]) -> str | None:
    for key in keys:
        value = os.environ.get(key, "")
        if value:
            return value
    return None


def probe_credentials_tier3(platform: str, root_dir: str, tier1_status: str) -> str:
    if tier1_status == "missing":
        return "missing"

    probe_file = Path(root_dir) / ".opencode-issue-probe"
    if not probe_file.exists():
        return tier1_status

    if platform == "github":
        try:
            result = subprocess.run(
                ["gh", "auth", "status"],
                capture_output=True,
                text=True,
                check=False,
                timeout=10,
            )
            if result.returncode == 0:
                return "verified"
            if result.returncode != 0 and "not logged in" in (result.stdout + result.stderr).lower():
                return "stale"
            return "stale"
        except (subprocess.SubprocessError, OSError):
            return tier1_status

    if platform == "gitbucket":
        try:
            result = subprocess.run(
                ["curl", "-sf", "-o", "/dev/null", "--max-time", "5", "http://localhost:8080/api/v3/"],
                capture_output=True,
                text=True,
                check=False,
                timeout=10,
            )
            if result.returncode == 0:
                return "verified"
            return "stale"
        except (subprocess.SubprocessError, OSError):
            return tier1_status

    return tier1_status


def detect_agent_binary() -> tuple[str, str]:
    """Detect the agent binary name and version from process arguments and environment.

    Co-authored with AI: OpenCode (ollama-cloud/glm-5.1)
    """
    import os
    import sys

    argv0 = sys.argv[0] if sys.argv else ""
    argv1 = sys.argv[1] if len(sys.argv) > 1 else ""

    for arg in [argv1, argv0]:
        if "opencode-cli" in arg:
            return "OpenCode CLI", ""
        if "opencode" in arg.lower() or "OpenCode" in arg:
            return "OpenCode", ""

    env_binary = os.environ.get("OPENCODE_BINARY", "")
    env_version = os.environ.get("OPENCODE_VERSION", "")

    if env_binary:
        return env_binary, env_version

    return "unknown (version detection failed)", ""


def build_identity_section(owner: str, repo: str, platform: str, credential_status: str) -> str:
    lines = [
        "## Repository Hosting Identity",
        f"- github.owner={owner}",
        f"- github.repo={repo}",
        f"- github.platform={platform}",
    ]
    cred_key = f"{platform.upper()}_CREDENTIALS" if platform != "unknown" else "CREDENTIALS"
    lines.append(f"- {cred_key}={credential_status}")
    lines.append("- Use these exact values for ALL GitHub MCP and GitBucket API calls")

    lines.append("")
    lines.append("## Target API Credentials")
    lines.append("- These are credentials for TARGET APIs the plugin operates on, NOT the repository hosting platform")
    lines.append("- Do NOT infer the hosting platform from these values")

    if credential_status == "missing":
        lines.append(f"- WARNING: No {platform} credentials found in .env, secrets.toml, or environment variables")
    elif credential_status == "stale":
        lines.append(
            f"- WARNING: {platform} token was rejected — "
            "check credentials in .env, secrets.toml, or environment variables"
        )

    return "\n".join(lines)


def main() -> int:
    remote_url = get_remote_url()
    if not remote_url:
        print("No git remote configured. Cannot determine repository identity.", file=sys.stderr)
        return 1

    root_dir = get_root_dir()
    if not root_dir:
        print("Not in a git repository.", file=sys.stderr)
        return 1

    platform = detect_platform(remote_url)
    owner, repo = parse_owner_repo(remote_url, platform)

    if not owner or not repo:
        print(f"Could not parse owner/repo from remote: {remote_url}", file=sys.stderr)
        return 1

    if platform == "unknown":
        owner, repo = parse_owner_repo(remote_url, "gitbucket")
        if not owner or not repo:
            print(f"Could not parse owner/repo from remote: {remote_url}", file=sys.stderr)
            return 1
        platform = "gitbucket"

    tier1 = probe_credentials_tier1(platform, root_dir)
    credential_status = probe_credentials_tier3(platform, root_dir, tier1)

    print(build_identity_section(owner, repo, platform, credential_status))

    agent_name, agent_version = detect_agent_binary()
    agent_line = f"AgentName: {agent_name}"
    if agent_version:
        agent_line += f"\nModelId: {agent_version}"
    print(agent_line)

    return 0


if __name__ == "__main__":
    sys.exit(main())
