# GitBucket Session Integration

## Overview

Session init script (`.opencode/tools/session-init`) provides GitBucket credentials from environment and git remote.

## Credential Sources (Priority Order)

Credentials are loaded in this order:

1. **Environment variables**
   ```bash
   export GITBUCKET_HTML_URL=https://gitbucket.example.com/gitbucket/
   export GITBUCKET_TOKEN=your-token
   ```

2. **Project .env file** (`<project>/.env`)
   ```bash
   # .env
   GITBUCKET_HTML_URL=https://gitbucket.example.com/gitbucket/
   GITBUCKET_TOKEN=your-token
   # NON-FUNCTIONAL: Basic auth is broken in GitBucket
   # GITBUCKET_USERNAME=admin
   # GITBUCKET_PASSWORD=password
   ```

3. **User config file** (platform-specific)
   - **Linux/macOS**: `~/.config/gitbucket/secrets.toml`
   - **Windows**: `%APPDATA%/gitbucket/secrets.toml`

## Create Config Template

If `secrets.toml` doesn't exist, create it using the CLI:

```bash
./.opencode/tools/gitbucket-api init-config
# Or specify a custom path:
./.opencode/tools/gitbucket-api init-config --path /custom/path/secrets.toml
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

```bash
# Validate credentials work
./.opencode/tools/gitbucket-api check-auth
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

## Credential Validation

```bash
# Validate token works
./.opencode/tools/gitbucket-api check-auth
```

## Best Practices

1. **Use config file** - Run `init-config` to create `secrets.toml` for persistent credentials
2. **Token auth ONLY** - Basic auth is broken in GitBucket, use token for all operations
3. **Error handling** - Check `check-auth` output for specific error types
4. **Cross-platform** - Config locations work on Linux, macOS, Windows
