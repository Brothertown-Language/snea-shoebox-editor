"""
GitBucket API Exception Classes

Provides exception hierarchy for GitBucket API errors.
"""

from typing import Optional


class GitBucketError(Exception):
    """Base exception for GitBucket API errors."""

    def __init__(self, code: int, message: str, endpoint: str):
        self.code = code
        self.message = message
        self.endpoint = endpoint
        super().__init__(f"HTTP {code} at {endpoint}: {message}")

    def __str__(self) -> str:
        return f"HTTP {self.code} at {self.endpoint}: {self.message}"


class AuthenticationError(GitBucketError):
    """401 Unauthorized - Authentication failed.

    Possible causes:
    - Invalid or expired token
    - Missing credentials
    - Basic auth used instead of token (use token auth)
    """

    def __init__(self, endpoint: str, message: str = "Unauthorized"):
        super().__init__(401, message, endpoint)


class NotFoundError(GitBucketError):
    """404 Not Found - Resource does not exist.

    Possible causes:
    - Wrong endpoint URL format
    - Repository not found
    - Issue/PR not found
    - User not found
    """

    def __init__(self, endpoint: str, message: str = "Not Found"):
        super().__init__(404, message, endpoint)


class ValidationError(GitBucketError):
    """422 Unprocessable Entity - Request validation failed.

    Possible causes:
    - Invalid request body format
    - Missing required fields
    - Invalid field values
    - Duplicate resource (e.g., label already exists)
    """

    def __init__(self, endpoint: str, message: str = "Validation Error"):
        super().__init__(422, message, endpoint)


class RateLimitError(GitBucketError):
    """403 Forbidden - Rate limit exceeded or forbidden.

    Possible causes:
    - Too many requests in short time
    - Insufficient permissions
    - Blocked by admin
    """

    def __init__(self, endpoint: str, message: str = "Rate Limit Exceeded"):
        super().__init__(403, message, endpoint)


class ServerError(GitBucketError):
    """5xx Server Error - GitBucket internal error.

    Possible causes:
    - GitBucket service unavailable
    - Database connection error
    - Internal server error
    """

    def __init__(self, code: int, endpoint: str, message: str = "Server Error"):
        if code < 500 or code >= 600:
            raise ValueError(f"Server error codes must be 5xx, got {code}")
        super().__init__(code, message, endpoint)


class MCPToolError(Exception):
    """MCP tool invocation failed.

    Used when gitbucket MCP tools fail and fallback to direct API is needed.
    This is NOT a GitBucket API error - it's a tool invocation error.
    """

    def __init__(self, tool: str, message: str):
        self.tool = tool
        self.message = message
        super().__init__(f"MCP tool {tool} failed: {message}")

    def __str__(self) -> str:
        return f"MCP tool {self.tool} failed: {self.message}"
