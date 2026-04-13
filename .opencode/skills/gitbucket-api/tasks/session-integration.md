# GitBucket Session Integration

## Overview

Session init script (`.opencode/tools/session-init`) provides GitBucket credentials from environment and git remote.

## Credential Sources (Priority Order)

Credentials are loaded in this order:

1. **Explicit parameters** - Highest priority
   ```python
   api = GitBucketAPI(
       url="https://gitbucket.example.com/gitbucket/",
       token="your-token"
   )
   ```

2. **Environment variables**
   ```bash
   export GITBUCKET_HTML_URL=https://gitbucket.example.com/gitbucket/
   export GITBUCKET_TOKEN=your-token
   ```

3. **Project .env file** (`<project>/.env`)
   ```bash
   # .env
   GITBUCKET_HTML_URL=https://gitbucket.example.com/gitbucket/
   GITBUCKET_TOKEN=your-token
   # NON-FUNCTIONAL: Basic auth is broken in GitBucket
   # GITBUCKET_USERNAME=admin
   # GITBUCKET_PASSWORD=password
   ```

4. **User config file** (platform-specific)
   - **Linux/macOS**: `~/.config/gitbucket/secrets.toml`
   - **Windows**: `%APPDATA%/gitbucket/secrets.toml`

## Create Config Template

If `secrets.toml` doesn't exist, create it automatically:

```python
from skills.gitbucket_api.tools import create_config_file

# Create platform-specific config file
config_path = create_config_file()
print(f"Config file created at: {config_path}")
```

**Or with API initialization:**

```python
from skills.gitbucket_api.tools import GitBucketAPI

# Create config template if missing
api = GitBucketAPI(create_config_if_missing=True)
```

**Template content:**

```toml
# GitBucket API Configuration
# This file stores your GitBucket credentials.
# 
# Get your token from: https://<gitbucket-url>/_settings/tokens
# 
# Fill in the values below:

# GitBucket base URL (required)
url = "https://gitbucket.example.com/gitbucket/"

# Personal access token (required for API operations)
token = "your-personal-access-token"

# Username for basic auth (NON-FUNCTIONAL: basic auth broken in GitBucket)
username = ""

# Password for basic auth (NON-FUNCTIONAL: basic auth broken in GitBucket)
password = ""

# Note: Token authentication is the ONLY working method.
# Basic auth returns "Bad credentials" for all requests.
```

## Platform-Specific Locations

| Platform | Config File Location |
|----------|---------------------|
| **Linux** | `~/.config/gitbucket/secrets.toml` |
| **macOS** | `~/.config/gitbucket/secrets.toml` |
| **Windows** | `%APPDATA%/gitbucket/secrets.toml` or `%LOCALAPPDATA%/gitbucket/secrets.toml` |

Note: Follows XDG Base Directory Specification. Respects `XDG_CONFIG_HOME` environment variable.

## Extract Credentials

```python
from skills.gitbucket_api.tools import GitBucketAPI

# Method 1: GitBucketAPI auto-detects
api = GitBucketAPI()  # Reads from .env, secrets.toml, env

# Method 2: Explicit create config
from skills.gitbucket_api.tools import create_config_file
config_path = create_config_file()
# Prints: "Created config at /home/user/.config/gitbucket/secrets.toml"
```

## Environment Variables

GitBucket credentials come from `.env` file:

```bash
# .env
GITBUCKET_HTML_URL=https://gitbucket.example.com/gitbucket/
GITBUCKET_TOKEN=your-personal-access-token
```

**Token vs Basic Auth:**

| Method | Use Case | Environment Variables | Status |
|--------|----------|----------------------|--------|
| Token | All operations | `GITBUCKET_TOKEN` | ✅ Working |
| Basic | Admin endpoints | `GITBUCKET_USERNAME`, `GITBUCKET_PASSWORD` | ❌ Broken |

## Platform Detection

```python
from skills.gitbucket_api.tools import is_gitbucket, is_github

if is_gitbucket():
    # Use GitBucket API
    api = GitBucketAPI()
    issue = api.create_issue(...)

elif is_github():
    # Use GitHub tools
    issue = github_issue_write(...)
```

## Repository Context

```python
from skills.gitbucket_api.tools import get_repo_context

context = get_repo_context()
# {'GIT_OWNER': 'myorg', 'GIT_REPO': 'myrepo', 'GIT_PLATFORM': 'gitbucket'}

# Use in API calls
api = GitBucketAPI()
issue = api.create_issue(
    owner=context['GIT_OWNER'],
    repo=context['GIT_REPO'],
    title="Bug report"
)
```

## Error Handling

```python
from skills.gitbucket_api.tools import GitBucketAPI
from skills.gitbucket_api.tools.exceptions import AuthenticationError

try:
    api = GitBucketAPI()  # Auto-detect from env/secrets.toml
except ValueError as e:
    # Missing GITBUCKET_URL
    print(f"Error: {e}")
    
try:
    api.get_current_user()
except AuthenticationError as e:
    # Invalid or expired token
    print(f"Auth failed: {e.message}")
```

## Credential Validation

```python
from skills.gitbucket_api.tools import GitBucketAPI

api = GitBucketAPI()

# Validate token works
try:
    user = api.get_current_user()
    print(f"Authenticated as {user['login']}")
except AuthenticationError:
    print("Token invalid or expired")
except NotFoundError:
    print("Wrong endpoint or GitBucket URL")
```

## Best Practices

1. **Use config file** - Create `secrets.toml` with `create_config_file()` for persistent credentials
2. **Token auth ONLY** - Basic auth is broken in GitBucket, use token for all operations
3. **Platform detection** - Check `is_gitbucket()` before GitBucket API calls
4. **Error handling** - Catch specific exceptions (AuthenticationError, NotFoundError, etc.)
5. **Cross-platform** - Config locations work on Linux, macOS, Windows

## Source Code

- `tools/auth.py` - Credential loading, platform-specific paths
- `tools/session.py` - Session integration
- `.opencode/tools/session-init` - Session init script

