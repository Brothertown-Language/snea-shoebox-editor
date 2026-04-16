# /// script
# requires-python = ">=3.12"
# dependencies = []
#
# [tool.uv]
# exclude-newer = "2026-04-14T00:00:00Z"
# ///

import argparse
import base64
import json
import os
import platform
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


class GitBucketError(Exception):
    def __init__(self, code: int, message: str, endpoint: str):
        self.code = code
        self.message = message
        self.endpoint = endpoint
        super().__init__(f"HTTP {code} at {endpoint}: {message}")

    def __str__(self) -> str:
        return f"HTTP {self.code} at {self.endpoint}: {self.message}"


class AuthenticationError(GitBucketError):
    def __init__(self, endpoint: str, message: str = "Unauthorized"):
        super().__init__(401, message, endpoint)


class NotFoundError(GitBucketError):
    def __init__(self, endpoint: str, message: str = "Not Found"):
        super().__init__(404, message, endpoint)


class ValidationError(GitBucketError):
    def __init__(self, endpoint: str, message: str = "Validation Error"):
        super().__init__(422, message, endpoint)


class RateLimitError(GitBucketError):
    def __init__(self, endpoint: str, message: str = "Rate Limit Exceeded"):
        super().__init__(403, message, endpoint)


class ServerError(GitBucketError):
    def __init__(self, code: int, endpoint: str, message: str = "Server Error"):
        if code < 500 or code >= 600:
            raise ValueError(f"Server error codes must be 5xx, got {code}")
        super().__init__(code, message, endpoint)


class MCPToolError(Exception):
    def __init__(self, tool: str, message: str):
        self.tool = tool
        self.message = message
        super().__init__(f"MCP tool {tool} failed: {message}")

    def __str__(self) -> str:
        return f"MCP tool {self.tool} failed: {self.message}"


def _get_config_file() -> Path:
    system = platform.system()
    if system == "Windows":
        appdata = os.environ.get("APPDATA") or os.environ.get("LOCALAPPDATA")
        if appdata:
            return Path(appdata) / "gitbucket" / "secrets.toml"
        return Path.home() / "AppData" / "Roaming" / "gitbucket" / "secrets.toml"
    elif system == "Darwin":
        xdg_config = os.environ.get("XDG_CONFIG_HOME")
        if xdg_config:
            return Path(xdg_config) / "gitbucket" / "secrets.toml"
        return Path.home() / ".config" / "gitbucket" / "secrets.toml"
    else:
        xdg_config = os.environ.get("XDG_CONFIG_HOME")
        if xdg_config:
            return Path(xdg_config) / "gitbucket" / "secrets.toml"
        return Path.home() / ".config" / "gitbucket" / "secrets.toml"


def _create_config_template(toml_path: Path | None = None) -> Path:
    if toml_path is None:
        toml_path = _get_config_file()
    if toml_path.exists():
        return toml_path
    toml_path.parent.mkdir(parents=True, exist_ok=True)
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


def _load_from_env_file(env_path: Path | None = None) -> dict[str, str]:
    if env_path is None:
        current = Path.cwd()
        while current != current.parent:
            if (current / ".git").exists():
                env_path = current / ".env"
                break
            current = current.parent
        else:
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


def _load_from_toml_file(toml_path: Path | None = None, create_if_missing: bool = False) -> dict[str, str]:
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
    token: str | None = None,
    username: str | None = None,
    password: str | None = None,
    url: str | None = None,
    create_config_if_missing: bool = False,
) -> dict[str, str | None]:
    creds = {
        "url": os.environ.get("GITBUCKET_HTML_URL") or os.environ.get("GITBUCKET_URL"),
        "token": os.environ.get("GITBUCKET_TOKEN"),
        "username": os.environ.get("GITBUCKET_USERNAME"),
        "password": os.environ.get("GITBUCKET_PASSWORD"),
    }
    env_file = _load_from_env_file()
    for key in creds:
        if key in env_file and creds.get(key) is None:
            creds[key] = env_file[key]
    toml_file = _load_from_toml_file(create_if_missing=create_config_if_missing)
    for key in creds:
        if key in toml_file and creds.get(key) is None:
            creds[key] = toml_file[key]
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
    def __init__(
        self,
        token: str | None = None,
        username: str | None = None,
        password: str | None = None,
        url: str | None = None,
        create_config_if_missing: bool = False,
    ):
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

    def get_headers(self, use_basic: bool = False) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if use_basic:
            if not self.username or not self.password:
                raise ValueError(
                    "Basic auth requires username and password. "
                    "Set GITBUCKET_USERNAME and GITBUCKET_PASSWORD in .env, "
                    "~/.config/gitbucket/secrets.toml, or environment variables."
                )
            credentials = base64.b64encode(f"{self.username}:{self.password}".encode()).decode()
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
        return bool(self.token)

    def has_basic(self) -> bool:
        return bool(self.username and self.password)

    def __repr__(self) -> str:
        methods = []
        if self.token:
            methods.append("token")
        if self.username and self.password:
            methods.append("basic")
        return f"GitBucketAuth(methods={methods})"


class GitBucketAPI:
    def __init__(
        self,
        url: str | None = None,
        token: str | None = None,
        username: str | None = None,
        password: str | None = None,
    ):
        creds = _get_credentials(token=token, username=username, password=password, url=url)
        self.url = creds["url"]
        if not self.url:
            raise ValueError(
                "GitBucket URL required. "
                "Set GITBUCKET_HTML_URL in:\n"
                "  - .env file (project root)\n"
                "  - ~/.config/gitbucket/secrets.toml\n"
                "  - environment variable\n"
                "Or pass url parameter."
            )
        if not self.url.endswith("/"):
            self.url += "/"
        self.auth = GitBucketAuth(
            token=creds["token"],
            username=creds["username"],
            password=creds["password"],
            url=creds["url"],
        )

    def _request(
        self,
        method: str,
        endpoint: str,
        data: dict[str, Any] | list[Any] | None = None,
        params: dict[str, str] | None = None,
        use_basic: bool = False,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        url = f"{self.url}api/v3{endpoint}"
        if params:
            param_str = "&".join(f"{k}={v}" for k, v in params.items())
            url += f"?{param_str}"
        try:
            headers = self.auth.get_headers(use_basic=use_basic)
        except ValueError as e:
            raise AuthenticationError(endpoint, str(e)) from e
        req = urllib.request.Request(url, method=method, headers=headers)
        if data is not None:
            req.data = json.dumps(data).encode("utf-8")
        try:
            with urllib.request.urlopen(req) as response:
                response_body = response.read().decode("utf-8")
                if response_body:
                    return json.loads(response_body)
                return {"status": "success"}
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8")
            error_message = error_body
            try:
                error_data = json.loads(error_body)
                if "message" in error_data:
                    error_message = error_data["message"]
            except json.JSONDecodeError:
                pass
            if e.code == 401:
                raise AuthenticationError(endpoint, error_message) from e
            elif e.code == 404:
                raise NotFoundError(endpoint, error_message) from e
            elif e.code == 422:
                raise ValidationError(endpoint, error_message) from e
            elif e.code == 403:
                raise RateLimitError(endpoint, error_message) from e
            elif 500 <= e.code < 600:
                raise ServerError(e.code, endpoint, error_message) from e
            else:
                raise GitBucketError(e.code, error_message, endpoint) from e

    def get(
        self,
        endpoint: str,
        params: dict[str, str] | None = None,
        use_basic: bool = False,
    ) -> dict[str, Any]:
        return self._request("GET", endpoint, params=params, use_basic=use_basic)

    def post(self, endpoint: str, data: dict[str, Any], use_basic: bool = False) -> dict[str, Any]:
        return self._request("POST", endpoint, data=data, use_basic=use_basic)

    def patch(self, endpoint: str, data: dict[str, Any], use_basic: bool = False) -> dict[str, Any]:
        return self._request("PATCH", endpoint, data=data, use_basic=use_basic)

    def put(
        self,
        endpoint: str,
        data: dict[str, Any] | None = None,
        use_basic: bool = False,
    ) -> dict[str, Any]:
        return self._request("PUT", endpoint, data=data, use_basic=use_basic)

    def delete(self, endpoint: str, use_basic: bool = False) -> dict[str, Any]:
        return self._request("DELETE", endpoint, use_basic=use_basic)

    def get_current_user(self) -> dict[str, Any]:
        return self.get("/user")

    def list_users(self) -> list[dict[str, Any]]:
        return self.get("/users")

    def get_user(self, username: str) -> dict[str, Any]:
        return self.get(f"/users/{username}")

    def list_user_repositories(self, username: str) -> list[dict[str, Any]]:
        return self.get(f"/users/{username}/repos")

    def list_own_repositories(self) -> list[dict[str, Any]]:
        return self.get("/user/repos")

    def create_repository(
        self,
        name: str,
        description: str | None = None,
        private: bool = False,
        auto_init: bool = False,
    ) -> dict[str, Any]:
        data = {
            "name": name,
            "description": description,
            "private": private,
            "auto_init": auto_init,
        }
        return self.post("/user/repos", {k: v for k, v in data.items() if v is not None})

    def create_org_repository(
        self,
        org: str,
        name: str,
        description: str | None = None,
        private: bool = False,
    ) -> dict[str, Any]:
        data = {"name": name, "description": description, "private": private}
        return self.post(f"/orgs/{org}/repos", {k: v for k, v in data.items() if v is not None})

    def get_repository(self, owner: str, repo: str) -> dict[str, Any]:
        return self.get(f"/repos/{owner}/{repo}")

    def list_issues(
        self,
        owner: str,
        repo: str,
        state: str | None = None,
        labels: str | None = None,
    ) -> list[dict[str, Any]]:
        params = {}
        if state:
            params["state"] = state
        if labels:
            params["labels"] = labels
        return self.get(f"/repos/{owner}/{repo}/issues", params=params if params else None)

    def create_issue(
        self,
        owner: str,
        repo: str,
        title: str,
        body: str | None = None,
        labels: list[str] | None = None,
        assignees: list[str] | None = None,
        milestone: int | None = None,
    ) -> dict[str, Any]:
        data = {
            "title": title,
            "body": body,
            "labels": labels or [],
            "assignees": assignees or [],
            "milestone": milestone,
        }
        return self.post(
            f"/repos/{owner}/{repo}/issues",
            {k: v for k, v in data.items() if v is not None},
        )

    def get_issue(self, owner: str, repo: str, issue_number: int) -> dict[str, Any]:
        return self.get(f"/repos/{owner}/{repo}/issues/{issue_number}")

    def update_issue(
        self,
        owner: str,
        repo: str,
        issue_number: int,
        title: str | None = None,
        body: str | None = None,
        state: str | None = None,
        labels: list[str] | None = None,
        assignees: list[str] | None = None,
        milestone: int | None = None,
    ) -> dict[str, Any]:
        data = {}
        if title is not None:
            data["title"] = title
        if body is not None:
            data["body"] = body
        if state is not None:
            data["state"] = state
        if labels is not None:
            data["labels"] = labels
        if assignees is not None:
            data["assignees"] = assignees
        if milestone is not None:
            data["milestone"] = milestone
        return self.patch(f"/repos/{owner}/{repo}/issues/{issue_number}", data)

    def add_issue_comment(self, owner: str, repo: str, issue_number: int, body: str) -> dict[str, Any]:
        return self.post(f"/repos/{owner}/{repo}/issues/{issue_number}/comments", {"body": body})

    def add_labels_to_issue(self, owner: str, repo: str, issue_number: int, labels: list[str]) -> list[dict[str, Any]]:
        return self.post(f"/repos/{owner}/{repo}/issues/{issue_number}/labels", labels)

    def replace_issue_labels(self, owner: str, repo: str, issue_number: int, labels: list[str]) -> list[dict[str, Any]]:
        return self.put(f"/repos/{owner}/{repo}/issues/{issue_number}/labels", labels)

    def remove_label_from_issue(self, owner: str, repo: str, issue_number: int, label_name: str) -> dict[str, Any]:
        return self.delete(f"/repos/{owner}/{repo}/issues/{issue_number}/labels/{label_name}")

    def remove_all_labels_from_issue(self, owner: str, repo: str, issue_number: int) -> dict[str, Any]:
        return self.delete(f"/repos/{owner}/{repo}/issues/{issue_number}/labels")

    def list_labels(self, owner: str, repo: str) -> list[dict[str, Any]]:
        return self.get(f"/repos/{owner}/{repo}/labels")

    def create_label(self, owner: str, repo: str, name: str, color: str) -> dict[str, Any]:
        return self.post(f"/repos/{owner}/{repo}/labels", {"name": name, "color": color})

    def list_pull_requests(
        self,
        owner: str,
        repo: str,
        state: str | None = None,
        head: str | None = None,
    ) -> list[dict[str, Any]]:
        params: dict[str, str] = {}
        if state:
            params["state"] = state
        if head:
            params["head"] = head
        return self.get(f"/repos/{owner}/{repo}/pulls", params=params if params else None)

    def create_pull_request(
        self,
        owner: str,
        repo: str,
        title: str,
        head: str,
        base: str,
        body: str | None = None,
        maintainer_can_modify: bool = True,
    ) -> dict[str, Any]:
        existing = self.list_pull_requests(owner, repo, state="open")
        for pr in existing:
            pr_head = pr.get("head", {})
            if isinstance(pr_head, dict):
                pr_ref = pr_head.get("ref", "") or pr_head.get("label", "")
            else:
                pr_ref = str(pr_head)
            if pr_ref == head:
                return pr
        data = {
            "title": title,
            "head": head,
            "base": base,
            "body": body,
            "maintainer_can_modify": maintainer_can_modify,
        }
        result = self.post(
            f"/repos/{owner}/{repo}/pulls",
            {k: v for k, v in data.items() if v is not None},
        )
        self._persist_pr_response(result)
        return result

    def _persist_pr_response(self, response: dict[str, Any]) -> None:
        tmp_dir = Path.cwd() / "tmp"
        tmp_dir.mkdir(parents=True, exist_ok=True)
        pr_file = tmp_dir / "pr-response.json"
        existing: list[dict[str, Any]] = []
        if pr_file.exists():
            try:
                existing = json.loads(pr_file.read_text(encoding="utf-8"))
                if not isinstance(existing, list):
                    existing = []
            except (json.JSONDecodeError, OSError):
                existing = []
        existing.append(response)
        pr_file.write_text(json.dumps(existing, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    def get_pull_request(self, owner: str, repo: str, pull_number: int) -> dict[str, Any]:
        return self.get(f"/repos/{owner}/{repo}/pulls/{pull_number}")

    def list_branches(self, owner: str, repo: str) -> list[dict[str, Any]]:
        return self.get(f"/repos/{owner}/{repo}/branches")

    def get_contents(
        self, owner: str, repo: str, path: str, ref: str | None = None
    ) -> dict[str, Any] | list[dict[str, Any]]:
        params = {"ref": ref} if ref else None
        return self.get(f"/repos/{owner}/{repo}/contents/{path}", params=params)

    def get_ref(self, owner: str, repo: str, ref: str) -> dict[str, Any]:
        return self.get(f"/repos/{owner}/{repo}/git/refs/{ref}")

    def create_status(
        self,
        owner: str,
        repo: str,
        sha: str,
        state: str,
        target_url: str | None = None,
        description: str | None = None,
        context: str | None = None,
    ) -> dict[str, Any]:
        data = {
            "state": state,
            "target_url": target_url,
            "description": description,
            "context": context,
        }
        return self.post(
            f"/repos/{owner}/{repo}/statuses/{sha}",
            {k: v for k, v in data.items() if v is not None},
        )

    def list_releases(self, owner: str, repo: str) -> list[dict[str, Any]]:
        return self.get(f"/repos/{owner}/{repo}/releases")

    def create_release(
        self,
        owner: str,
        repo: str,
        tag_name: str,
        target_commitish: str | None = None,
        name: str | None = None,
        body: str | None = None,
        draft: bool = False,
        prerelease: bool = False,
    ) -> dict[str, Any]:
        data = {
            "tag_name": tag_name,
            "target_commitish": target_commitish,
            "name": name,
            "body": body,
            "draft": draft,
            "prerelease": prerelease,
        }
        return self.post(
            f"/repos/{owner}/{repo}/releases",
            {k: v for k, v in data.items() if v is not None},
        )

    def list_milestones(self, owner: str, repo: str) -> list[dict[str, Any]]:
        return self.get(f"/repos/{owner}/{repo}/milestones")

    def create_milestone(
        self,
        owner: str,
        repo: str,
        title: str,
        state: str | None = None,
        description: str | None = None,
        due_on: str | None = None,
    ) -> dict[str, Any]:
        data = {
            "title": title,
            "state": state,
            "description": description,
            "due_on": due_on,
        }
        return self.post(
            f"/repos/{owner}/{repo}/milestones",
            {k: v for k, v in data.items() if v is not None},
        )

    def list_webhooks(self, owner: str, repo: str) -> list[dict[str, Any]]:
        return self.get(f"/repos/{owner}/{repo}/hooks")

    def create_webhook(
        self,
        owner: str,
        repo: str,
        name: str,
        config: dict[str, Any],
        events: list[str] | None = None,
        active: bool = True,
    ) -> dict[str, Any]:
        data = {
            "name": name,
            "config": config,
            "events": events or ["push"],
            "active": active,
        }
        return self.post(f"/repos/{owner}/{repo}/hooks", data)

    def create_user(self, username: str, password: str, email: str, is_admin: bool = False) -> dict[str, Any]:
        data = {
            "username": username,
            "password": password,
            "email": email,
            "is_admin": is_admin,
        }
        return self.post("/admin/users", data, use_basic=True)

    def create_organization(self, name: str, description: str | None = None) -> dict[str, Any]:
        data = {"name": name, "description": description}
        return self.post(
            "/admin/organizations",
            {k: v for k, v in data.items() if v is not None},
            use_basic=True,
        )


def _json_output(data: Any) -> None:
    print(json.dumps(data, indent=2, ensure_ascii=False))


def _make_api(args: argparse.Namespace) -> GitBucketAPI:
    return GitBucketAPI(
        url=getattr(args, "url", None),
        token=getattr(args, "token", None),
        username=getattr(args, "username", None),
        password=getattr(args, "password", None),
    )


def _add_auth_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--url", help="GitBucket base URL")
    parser.add_argument("--token", help="GitBucket personal access token")
    parser.add_argument("--username", help="Username for basic auth")
    parser.add_argument("--password", help="Password for basic auth")


def _cmd_me(args: argparse.Namespace) -> None:
    api = _make_api(args)
    _json_output(api.get_current_user())


def _cmd_list_issues(args: argparse.Namespace) -> None:
    api = _make_api(args)
    _json_output(api.list_issues(args.owner, args.repo, state=args.state))


def _cmd_get_issue(args: argparse.Namespace) -> None:
    api = _make_api(args)
    _json_output(api.get_issue(args.owner, args.repo, args.number))


def _cmd_create_issue(args: argparse.Namespace) -> None:
    api = _make_api(args)
    labels = args.labels.split(",") if args.labels else None
    _json_output(api.create_issue(args.owner, args.repo, args.title, body=args.body, labels=labels))


def _cmd_add_comment(args: argparse.Namespace) -> None:
    api = _make_api(args)
    _json_output(api.add_issue_comment(args.owner, args.repo, args.number, args.body))


def _cmd_list_prs(args: argparse.Namespace) -> None:
    api = _make_api(args)
    _json_output(api.list_pull_requests(args.owner, args.repo, state=args.state, head=args.head))


def _cmd_create_pr(args: argparse.Namespace) -> None:
    api = _make_api(args)
    _json_output(api.create_pull_request(args.owner, args.repo, args.title, args.head, args.base, body=args.body))


def _cmd_list_labels(args: argparse.Namespace) -> None:
    api = _make_api(args)
    _json_output(api.list_labels(args.owner, args.repo))


def _cmd_list_branches(args: argparse.Namespace) -> None:
    api = _make_api(args)
    _json_output(api.list_branches(args.owner, args.repo))


def _cmd_list_repos(args: argparse.Namespace) -> None:
    api = _make_api(args)
    if args.user:
        _json_output(api.list_user_repositories(args.user))
    else:
        _json_output(api.list_own_repositories())


def _cmd_get_repo(args: argparse.Namespace) -> None:
    api = _make_api(args)
    _json_output(api.get_repository(args.owner, args.repo))


def _cmd_init_config(args: argparse.Namespace) -> None:
    path = _create_config_template()
    print(f"Config file at: {path}")


def _cmd_check_auth(args: argparse.Namespace) -> None:
    api = _make_api(args)
    try:
        user = api.get_current_user()
        print(f"Authenticated as: {user.get('login', 'unknown')}")
    except AuthenticationError:
        print("Authentication failed: invalid or missing token")
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="gitbucket-api",
        description="GitBucket API CLI client (PEP 723 self-contained)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_me = sub.add_parser("me", help="Get authenticated user")
    _add_auth_args(p_me)

    p_issues = sub.add_parser("issues", help="List repository issues")
    p_issues.add_argument("owner", help="Repository owner")
    p_issues.add_argument("repo", help="Repository name")
    p_issues.add_argument("--state", help="Filter: open, closed, all")
    _add_auth_args(p_issues)

    p_issue = sub.add_parser("issue", help="Get issue details")
    p_issue.add_argument("owner", help="Repository owner")
    p_issue.add_argument("repo", help="Repository name")
    p_issue.add_argument("number", type=int, help="Issue number")
    _add_auth_args(p_issue)

    p_create = sub.add_parser("create-issue", help="Create issue")
    p_create.add_argument("owner", help="Repository owner")
    p_create.add_argument("repo", help="Repository name")
    p_create.add_argument("title", help="Issue title")
    p_create.add_argument("--body", help="Issue body")
    p_create.add_argument("--labels", help="Comma-separated label names")
    _add_auth_args(p_create)

    p_comment = sub.add_parser("add-comment", help="Add comment to issue")
    p_comment.add_argument("owner", help="Repository owner")
    p_comment.add_argument("repo", help="Repository name")
    p_comment.add_argument("number", type=int, help="Issue number")
    p_comment.add_argument("body", help="Comment body")
    _add_auth_args(p_comment)

    p_prs = sub.add_parser("prs", help="List pull requests")
    p_prs.add_argument("owner", help="Repository owner")
    p_prs.add_argument("repo", help="Repository name")
    p_prs.add_argument("--state", help="Filter: open, closed, all")
    p_prs.add_argument("--head", help="Filter by head branch ref")
    _add_auth_args(p_prs)

    p_create_pr = sub.add_parser("create-pr", help="Create pull request")
    p_create_pr.add_argument("owner", help="Repository owner")
    p_create_pr.add_argument("repo", help="Repository name")
    p_create_pr.add_argument("title", help="PR title")
    p_create_pr.add_argument("head", help="Source branch")
    p_create_pr.add_argument("base", help="Target branch")
    p_create_pr.add_argument("--body", help="PR body")
    _add_auth_args(p_create_pr)

    p_labels = sub.add_parser("labels", help="List repository labels")
    p_labels.add_argument("owner", help="Repository owner")
    p_labels.add_argument("repo", help="Repository name")
    _add_auth_args(p_labels)

    p_branches = sub.add_parser("branches", help="List repository branches")
    p_branches.add_argument("owner", help="Repository owner")
    p_branches.add_argument("repo", help="Repository name")
    _add_auth_args(p_branches)

    p_repos = sub.add_parser("repos", help="List repositories")
    p_repos.add_argument("--user", help="Username (default: authenticated user)")
    _add_auth_args(p_repos)

    p_repo = sub.add_parser("repo", help="Get repository details")
    p_repo.add_argument("owner", help="Repository owner")
    p_repo.add_argument("repo", help="Repository name")
    _add_auth_args(p_repo)

    p_init = sub.add_parser("init-config", help="Create secrets.toml template")
    p_init.add_argument("--path", type=Path, help="Custom path (default: platform-specific)")

    p_check = sub.add_parser("check-auth", help="Verify authentication works")
    _add_auth_args(p_check)

    args = parser.parse_args()

    commands = {
        "me": _cmd_me,
        "issues": _cmd_list_issues,
        "issue": _cmd_get_issue,
        "create-issue": _cmd_create_issue,
        "add-comment": _cmd_add_comment,
        "prs": _cmd_list_prs,
        "create-pr": _cmd_create_pr,
        "labels": _cmd_list_labels,
        "branches": _cmd_list_branches,
        "repos": _cmd_list_repos,
        "repo": _cmd_get_repo,
        "init-config": _cmd_init_config,
        "check-auth": _cmd_check_auth,
    }

    cmd_func = commands.get(args.command)
    if cmd_func:
        cmd_func(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
