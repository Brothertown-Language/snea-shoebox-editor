"""
GitBucket API Core Client

Pure-stdlib GitBucket API client using urllib.
Implements all 32 endpoints from OpenAPI v4.42.1.

NO external dependencies - uses only Python stdlib.

Usage:
    from skills.gitbucket_api.tools import GitBucketAPI

    # Initialize with environment variables
    api = GitBucketAPI()

    # Or with explicit credentials
    api = GitBucketAPI(
        url="https://gitbucket.example.com/gitbucket/",
        token="your-token"
    )

    # Issue operations
    issue = api.issues.create(owner="org", repo="project", title="Bug")
    issue = api.issues.get(owner="org", repo="project", issue_number=14)

    # PR operations
    pr = api.pull_requests.create(owner="org", repo="project", title="Feature", head="branch", base="main")
"""

import json
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional, Union

from .auth import GitBucketAuth, _get_credentials
from .exceptions import (
    AuthenticationError,
    GitBucketError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
)


class GitBucketAPI:
    """GitBucket API client using urllib (stdlib only).

    Implements all 32 endpoints from OpenAPI v4.42.1 specification.

    Authentication: Token auth ONLY. Basic auth is broken in GitBucket
    ("Bad credentials" error) — username/password parameters are retained
    for forward-compatibility only.

    Categories:
        - Users & Auth (5 methods)
        - Repositories (4 methods)
        - Issues (4 methods)
        - Pull Requests (4 methods)
        - Branches (1 method)
        - Contents (1 method)
        - Git Data (2 methods)
        - Releases (2 methods)
        - Labels (2 methods)
        - Milestones (2 methods)
        - Webhooks (2 methods)
        - Admin (2 methods)

    Authentication:
        Token auth (default): Authorization: token {TOKEN}
        Basic auth (admin): Authorization: Basic {base64(user:pass)}
    """

    def __init__(
        self,
        url: Optional[str] = None,
        token: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ):
        """Initialize GitBucket API client.

        Args:
            url: GitBucket base URL
            token: Personal access token
            username: Username for basic auth (NON-FUNCTIONAL: basic auth broken)
            password: Password for basic auth (NON-FUNCTIONAL: basic auth broken)

        Note:
            Credentials are loaded in priority order:
            1. Explicit parameters (url, token, username, password)
            2. Environment variables (GITBUCKET_HTML_URL, GITBUCKET_TOKEN, etc.)
            3. Project .env file (<project>/.env)
            4. User config file (~/.config/gitbucket/secrets.toml)

        Examples:
            # From .env/secrets.toml/environment (recommended)
            api = GitBucketAPI()

            # With explicit URL and token
            api = GitBucketAPI(
                url="https://gitbucket.example.com/gitbucket/",
                token="your-token"
            )
        """
        # Get credentials from all sources
        creds = _get_credentials(
            token=token, username=username, password=password, url=url
        )

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

        # Ensure URL ends with /
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
        data: Optional[Union[Dict[str, Any], List[Any]]] = None,
        params: Optional[Dict[str, str]] = None,
        use_basic: bool = False,
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """Make HTTP request to GitBucket API.

        Args:
            method: HTTP method (GET, POST, PATCH, PUT, DELETE)
            endpoint: API endpoint (e.g., /repos/{owner}/{repo}/issues)
            data: Request body (for POST/PATCH/PUT)
            params: Query parameters (for GET)
            use_basic: Use basic auth instead of token (for admin endpoints)

        Returns:
            Response data as dict

        Raises:
            AuthenticationError: 401 Unauthorized
            NotFoundError: 404 Not Found
            ValidationError: 422 Unprocessable Entity
            RateLimitError: 403 Forbidden
            ServerError: 5xx Server Error
            GitBucketError: Other HTTP errors

        Note:
            This method handles all HTTP requests internally.
            Use convenience methods (get, post, patch, put, delete) instead.
        """
        # Build URL
        url = f"{self.url}api/v3{endpoint}"

        # Add query parameters
        if params:
            param_str = "&".join(f"{k}={v}" for k, v in params.items())
            url += f"?{param_str}"

        # Get headers
        try:
            headers = self.auth.get_headers(use_basic=use_basic)
        except ValueError as e:
            raise AuthenticationError(endpoint, str(e))

        # Build request
        req = urllib.request.Request(url, method=method, headers=headers)

        # Add body
        if data is not None:
            req.data = json.dumps(data).encode("utf-8")

        # Make request
        try:
            with urllib.request.urlopen(req) as response:
                response_body = response.read().decode("utf-8")
                if response_body:
                    return json.loads(response_body)
                return {"status": "success"}

        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8")
            error_message = error_body

            # Try to parse error message
            try:
                error_data = json.loads(error_body)
                if "message" in error_data:
                    error_message = error_data["message"]
            except json.JSONDecodeError:
                pass

            # Map status codes to exceptions
            if e.code == 401:
                raise AuthenticationError(endpoint, error_message)
            elif e.code == 404:
                raise NotFoundError(endpoint, error_message)
            elif e.code == 422:
                raise ValidationError(endpoint, error_message)
            elif e.code == 403:
                raise RateLimitError(endpoint, error_message)
            elif 500 <= e.code < 600:
                raise ServerError(e.code, endpoint, error_message)
            else:
                raise GitBucketError(e.code, error_message, endpoint)

    # Convenience methods

    def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, str]] = None,
        use_basic: bool = False,
    ) -> Dict[str, Any]:
        """GET request to GitBucket API.

        Args:
            endpoint: API endpoint
            params: Query parameters
            use_basic: Use basic auth (for admin endpoints)

        Returns:
            Response data
        """
        return self._request("GET", endpoint, params=params, use_basic=use_basic)

    def post(
        self, endpoint: str, data: Dict[str, Any], use_basic: bool = False
    ) -> Dict[str, Any]:
        """POST request to GitBucket API.

        Args:
            endpoint: API endpoint
            data: Request body
            use_basic: Use basic auth (for admin endpoints)

        Returns:
            Response data
        """
        return self._request("POST", endpoint, data=data, use_basic=use_basic)

    def patch(
        self, endpoint: str, data: Dict[str, Any], use_basic: bool = False
    ) -> Dict[str, Any]:
        """PATCH request to GitBucket API.

        Args:
            endpoint: API endpoint
            data: Request body
            use_basic: Use basic auth (for admin endpoints)

        Returns:
            Response data
        """
        return self._request("PATCH", endpoint, data=data, use_basic=use_basic)

    def put(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        use_basic: bool = False,
    ) -> Dict[str, Any]:
        """PUT request to GitBucket API.

        Args:
            endpoint: API endpoint
            data: Request body (optional)
            use_basic: Use basic auth (for admin endpoints)

        Returns:
            Response data
        """
        return self._request("PUT", endpoint, data=data, use_basic=use_basic)

    def delete(self, endpoint: str, use_basic: bool = False) -> Dict[str, Any]:
        """DELETE request to GitBucket API.

        Args:
            endpoint: API endpoint
            use_basic: Use basic auth (for admin endpoints)

        Returns:
            Response data
        """
        return self._request("DELETE", endpoint, use_basic=use_basic)

    # User operations

    def get_current_user(self) -> Dict[str, Any]:
        """Get authenticated user.

        Returns:
            User object with login, id, email, etc.
        """
        return self.get("/user")

    def list_users(self) -> List[Dict[str, Any]]:
        """List all users.

        Returns:
            List of user objects
        """
        return self.get("/users")

    def get_user(self, username: str) -> Dict[str, Any]:
        """Get user by username.

        Args:
            username: GitBucket username

        Returns:
            User object
        """
        return self.get(f"/users/{username}")

    def list_user_repositories(self, username: str) -> List[Dict[str, Any]]:
        """List repositories for a user.

        Args:
            username: GitBucket username

        Returns:
            List of repository objects
        """
        return self.get(f"/users/{username}/repos")

    def list_own_repositories(self) -> List[Dict[str, Any]]:
        """List repositories for authenticated user.

        Returns:
            List of repository objects
        """
        return self.get("/user/repos")

    # Repository operations

    def create_repository(
        self,
        name: str,
        description: Optional[str] = None,
        private: bool = False,
        auto_init: bool = False,
    ) -> Dict[str, Any]:
        """Create repository for authenticated user.

        Args:
            name: Repository name
            description: Repository description
            private: Whether repository is private
            auto_init: Initialize with README

        Returns:
            Created repository object
        """
        data = {
            "name": name,
            "description": description,
            "private": private,
            "auto_init": auto_init,
        }
        return self.post(
            "/user/repos", {k: v for k, v in data.items() if v is not None}
        )

    def create_org_repository(
        self,
        org: str,
        name: str,
        description: Optional[str] = None,
        private: bool = False,
    ) -> Dict[str, Any]:
        """Create repository in organization.

        Args:
            org: Organization name
            name: Repository name
            description: Repository description
            private: Whether repository is private

        Returns:
            Created repository object
        """
        data = {"name": name, "description": description, "private": private}
        return self.post(
            f"/orgs/{org}/repos", {k: v for k, v in data.items() if v is not None}
        )

    def get_repository(self, owner: str, repo: str) -> Dict[str, Any]:
        """Get repository details.

        Args:
            owner: Repository owner
            repo: Repository name

        Returns:
            Repository object
        """
        return self.get(f"/repos/{owner}/{repo}")

    # Issue operations

    def list_issues(
        self,
        owner: str,
        repo: str,
        state: Optional[str] = None,
        labels: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List repository issues.

        Args:
            owner: Repository owner
            repo: Repository name
            state: Filter by state ('open', 'closed', 'all')
            labels: Filter by labels (comma-separated)

        Returns:
            List of issue objects
        """
        params = {}
        if state:
            params["state"] = state
        if labels:
            params["labels"] = labels
        return self.get(
            f"/repos/{owner}/{repo}/issues", params=params if params else None
        )

    def create_issue(
        self,
        owner: str,
        repo: str,
        title: str,
        body: Optional[str] = None,
        labels: Optional[List[str]] = None,
        assignees: Optional[List[str]] = None,
        milestone: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Create issue.

        Args:
            owner: Repository owner
            repo: Repository name
            title: Issue title
            body: Issue body/description
            labels: Label names (auto-created if missing)
            assignees: Assignee usernames
            milestone: Milestone number

        Returns:
            Created issue object
        """
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

    def get_issue(self, owner: str, repo: str, issue_number: int) -> Dict[str, Any]:
        """Get issue details.

        Args:
            owner: Repository owner
            repo: Repository name
            issue_number: Issue number

        Returns:
            Issue object
        """
        return self.get(f"/repos/{owner}/{repo}/issues/{issue_number}")

    def update_issue(
        self,
        owner: str,
        repo: str,
        issue_number: int,
        title: Optional[str] = None,
        body: Optional[str] = None,
        state: Optional[str] = None,
        labels: Optional[List[str]] = None,
        assignees: Optional[List[str]] = None,
        milestone: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Update issue.

        Args:
            owner: Repository owner
            repo: Repository name
            issue_number: Issue number
            title: New title
            body: New body
            state: New state ('open' or 'closed')
            labels: Replace labels
            assignees: Replace assignees
            milestone: Milestone number

        Returns:
            Updated issue object
        """
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

    def add_issue_comment(
        self, owner: str, repo: str, issue_number: int, body: str
    ) -> Dict[str, Any]:
        """Add comment to issue.

        Args:
            owner: Repository owner
            repo: Repository name
            issue_number: Issue number
            body: Comment body

        Returns:
            Created comment object
        """
        return self.post(
            f"/repos/{owner}/{repo}/issues/{issue_number}/comments", {"body": body}
        )

    # Label operations (on issues)

    def add_labels_to_issue(
        self, owner: str, repo: str, issue_number: int, labels: List[str]
    ) -> List[Dict[str, Any]]:
        """Add labels to issue (auto-creates missing labels).

        Args:
            owner: Repository owner
            repo: Repository name
            issue_number: Issue number
            labels: Label names to add

        Returns:
            List of label objects (including auto-created labels)

        Note:
            GitBucket auto-creates labels that don't exist (unlike GitHub).
        """
        return self.post(f"/repos/{owner}/{repo}/issues/{issue_number}/labels", labels)

    def replace_issue_labels(
        self, owner: str, repo: str, issue_number: int, labels: List[str]
    ) -> List[Dict[str, Any]]:
        """Replace all labels on issue.

        Args:
            owner: Repository owner
            repo: Repository name
            issue_number: Issue number
            labels: New label names (replaces all existing labels)

        Returns:
            List of label objects
        """
        return self.put(f"/repos/{owner}/{repo}/issues/{issue_number}/labels", labels)

    def remove_label_from_issue(
        self, owner: str, repo: str, issue_number: int, label_name: str
    ) -> Dict[str, Any]:
        """Remove specific label from issue.

        Args:
            owner: Repository owner
            repo: Repository name
            issue_number: Issue number
            label_name: Label name to remove

        Returns:
            Empty response on success
        """
        return self.delete(
            f"/repos/{owner}/{repo}/issues/{issue_number}/labels/{label_name}"
        )

    def remove_all_labels_from_issue(
        self, owner: str, repo: str, issue_number: int
    ) -> Dict[str, Any]:
        """Remove all labels from issue.

        Args:
            owner: Repository owner
            repo: Repository name
            issue_number: Issue number

        Returns:
            Empty response on success
        """
        return self.delete(f"/repos/{owner}/{repo}/issues/{issue_number}/labels")

    # Repository label operations

    def list_labels(self, owner: str, repo: str) -> List[Dict[str, Any]]:
        """List all repository labels.

        Args:
            owner: Repository owner
            repo: Repository name

        Returns:
            List of label objects
        """
        return self.get(f"/repos/{owner}/{repo}/labels")

    def create_label(
        self, owner: str, repo: str, name: str, color: str
    ) -> Dict[str, Any]:
        """Create repository label.

        Args:
            owner: Repository owner
            repo: Repository name
            name: Label name
            color: Hex color code (e.g., 'ff0000')

        Returns:
            Created label object
        """
        return self.post(
            f"/repos/{owner}/{repo}/labels", {"name": name, "color": color}
        )

    # Pull request operations

    def list_pull_requests(
        self, owner: str, repo: str, state: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List pull requests.

        Args:
            owner: Repository owner
            repo: Repository name
            state: Filter by state ('open', 'closed', 'all')

        Returns:
            List of pull request objects
        """
        params = {"state": state} if state else None
        return self.get(f"/repos/{owner}/{repo}/pulls", params=params)

    def create_pull_request(
        self,
        owner: str,
        repo: str,
        title: str,
        head: str,
        base: str,
        body: Optional[str] = None,
        maintainer_can_modify: bool = True,
    ) -> Dict[str, Any]:
        """Create pull request.

        Args:
            owner: Repository owner
            repo: Repository name
            title: Pull request title
            head: Source branch (user:branch for cross-repo)
            base: Target branch
            body: Pull request description
            maintainer_can_modify: Allow maintainer edits

        Returns:
            Created pull request object
        """
        data = {
            "title": title,
            "head": head,
            "base": base,
            "body": body,
            "maintainer_can_modify": maintainer_can_modify,
        }
        return self.post(
            f"/repos/{owner}/{repo}/pulls",
            {k: v for k, v in data.items() if v is not None},
        )

    def get_pull_request(
        self, owner: str, repo: str, pull_number: int
    ) -> Dict[str, Any]:
        """Get pull request details.

        Args:
            owner: Repository owner
            repo: Repository name
            pull_number: Pull request number

        Returns:
            Pull request object
        """
        return self.get(f"/repos/{owner}/{repo}/pulls/{pull_number}")

    # Branch operations

    def list_branches(self, owner: str, repo: str) -> List[Dict[str, Any]]:
        """List repository branches.

        Args:
            owner: Repository owner
            repo: Repository name

        Returns:
            List of branch objects
        """
        return self.get(f"/repos/{owner}/{repo}/branches")

    # Content operations

    def get_contents(
        self, owner: str, repo: str, path: str, ref: Optional[str] = None
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """Get repository content (file or directory).

        Args:
            owner: Repository owner
            repo: Repository name
            path: File path
            ref: Branch or commit SHA

        Returns:
            File object or list of directory objects
        """
        params = {"ref": ref} if ref else None
        return self.get(f"/repos/{owner}/{repo}/contents/{path}", params=params)

    # Git data operations

    def get_ref(self, owner: str, repo: str, ref: str) -> Dict[str, Any]:
        """Get Git reference (branch, tag, or commit).

        Args:
            owner: Repository owner
            repo: Repository name
            ref: Reference name (e.g., 'heads/main', 'tags/v1.0.0')

        Returns:
            Git reference object
        """
        return self.get(f"/repos/{owner}/{repo}/git/refs/{ref}")

    def create_status(
        self,
        owner: str,
        repo: str,
        sha: str,
        state: str,
        target_url: Optional[str] = None,
        description: Optional[str] = None,
        context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create commit status.

        Args:
            owner: Repository owner
            repo: Repository name
            sha: Commit SHA
            state: Status state ('pending', 'success', 'error', 'failure')
            target_url: Target URL for details
            description: Status description
            context: Status context

        Returns:
            Created status object
        """
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

    # Release operations

    def list_releases(self, owner: str, repo: str) -> List[Dict[str, Any]]:
        """List repository releases.

        Args:
            owner: Repository owner
            repo: Repository name

        Returns:
            List of release objects
        """
        return self.get(f"/repos/{owner}/{repo}/releases")

    def create_release(
        self,
        owner: str,
        repo: str,
        tag_name: str,
        target_commitish: Optional[str] = None,
        name: Optional[str] = None,
        body: Optional[str] = None,
        draft: bool = False,
        prerelease: bool = False,
    ) -> Dict[str, Any]:
        """Create release.

        Args:
            owner: Repository owner
            repo: Repository name
            tag_name: Tag name (e.g., 'v1.0.0')
            target_commitish: Target branch or commit
            name: Release name
            body: Release description
            draft: Whether release is draft
            prerelease: Whether release is prerelease

        Returns:
            Created release object
        """
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

    # Milestone operations

    def list_milestones(self, owner: str, repo: str) -> List[Dict[str, Any]]:
        """List repository milestones.

        Args:
            owner: Repository owner
            repo: Repository name

        Returns:
            List of milestone objects
        """
        return self.get(f"/repos/{owner}/{repo}/milestones")

    def create_milestone(
        self,
        owner: str,
        repo: str,
        title: str,
        state: Optional[str] = None,
        description: Optional[str] = None,
        due_on: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create milestone.

        Args:
            owner: Repository owner
            repo: Repository name
            title: Milestone title
            state: Milestone state ('open' or 'closed')
            description: Milestone description
            due_on: Due date (ISO 8601 format)

        Returns:
            Created milestone object
        """
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

    # Webhook operations

    def list_webhooks(self, owner: str, repo: str) -> List[Dict[str, Any]]:
        """List repository webhooks.

        Args:
            owner: Repository owner
            repo: Repository name

        Returns:
            List of webhook objects
        """
        return self.get(f"/repos/{owner}/{repo}/hooks")

    def create_webhook(
        self,
        owner: str,
        repo: str,
        name: str,
        config: Dict[str, Any],
        events: Optional[List[str]] = None,
        active: bool = True,
    ) -> Dict[str, Any]:
        """Create repository webhook.

        Args:
            owner: Repository owner
            repo: Repository name
            name: Webhook name (usually 'web')
            config: Webhook config (url, content_type, secret)
            events: Event types (e.g., ['push', 'pull_request'])
            active: Whether webhook is active

        Returns:
            Created webhook object
        """
        data = {
            "name": name,
            "config": config,
            "events": events or ["push"],
            "active": active,
        }
        return self.post(f"/repos/{owner}/{repo}/hooks", data)

    # Admin operations (require Basic auth)

    def create_user(
        self, username: str, password: str, email: str, is_admin: bool = False
    ) -> Dict[str, Any]:
        """Create user account (admin only, requires Basic auth).

        Args:
            username: Username
            password: Password
            email: Email address
            is_admin: Whether user is admin

        Returns:
            Created user object

        Note:
            This endpoint requires Basic authentication.
            Initialize GitBucketAPI with username and password.
        """
        data = {
            "username": username,
            "password": password,
            "email": email,
            "is_admin": is_admin,
        }
        return self.post("/admin/users", data, use_basic=True)

    def create_organization(
        self, name: str, description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create organization (admin only, requires Basic auth).

        Args:
            name: Organization name
            description: Organization description

        Returns:
            Created organization object

        Note:
            This endpoint requires Basic authentication.
            Initialize GitBucketAPI with username and password.
        """
        data = {"name": name, "description": description}
        return self.post(
            "/admin/organizations",
            {k: v for k, v in data.items() if v is not None},
            use_basic=True,
        )
