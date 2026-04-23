# Runbook: GitHub PAT Setup for OpenCode GitHub MCP

**Purpose**: Create and configure a GitHub Personal Access Token for the OpenCode GitHub MCP plugin.

**Audience**: Developer with admin access to the Brothertown-Language GitHub organization.

---

## Phase 1: Create a Classic Personal Access Token

### 1.1 Navigate to token creation

1. Verify your email address: https://github.com/settings/emails
2. Go to: https://github.com/settings/tokens
3. In the left sidebar, under **Personal access tokens**, click **Tokens (classic)**
4. Click **Generate new token** → **Generate new token (classic)**

### 1.2 Configure the token

| Field | Value |
|-------|-------|
| Note | `opencode-mcp` |
| Expiration | 90 days |

### 1.3 Select scopes (checkboxes)

Check these scopes, grouped by the MCP toolset or feature they enable:

#### Repository and code operations (required)

| Scope | Toolset / Feature | What it enables |
|-------|-------------------|-----------------|
| `repo` | repos, issues, pull_requests, actions, discussions, context, git, copilot | Read/write code, issues, PRs, commits, releases, commit statuses, deployments, webhooks, file contents, code search, sub-issues, Copilot review assignment, repository trees |
| `workflow` | actions | Create and update GitHub Actions workflow files |

#### Organization management (required)

| Scope | Toolset / Feature | What it enables |
|-------|-------------------|-----------------|
| `admin:org` | orgs, context (team tools), issues (issue types) | Read and write org membership, teams, and settings; create repositories under the org; manage org-level resources; list organization issue types |

> `admin:org` includes `read:org` and `write:org` — no need to check those separately.

#### Security (required)

| Scope | Toolset / Feature | What it enables |
|-------|-------------------|-----------------|
| `security_events` | code_security, dependabot, secret_protection, security_advisories | Read code scanning alerts, Dependabot alerts, secret scanning alerts, global and repository security advisories |

#### Notifications (required)

| Scope | Toolset / Feature | What it enables |
|-------|-------------------|-----------------|
| `notifications` | notifications | List/read/dismiss notifications; manage notification subscriptions for repositories |

#### Project management (optional)

| Scope | Toolset / Feature | What it enables |
|-------|-------------------|-----------------|
| `read:project` | projects | Read and list GitHub Projects, project items, and fields |
| `project` | projects | Write to Projects — create/update/delete project items and fields |

> Check both if you use GitHub Projects; check only `read:project` for read-only access.

#### Gists (optional)

| Scope | Toolset / Feature | What it enables |
|-------|-------------------|-----------------|
| `gist` | gists | Create and update gists |

#### Minimum required scopes

For full OpenCode MCP functionality, check these scopes:

- `repo`
- `admin:org`
- `workflow`
- `security_events`
- `notifications`

For optional features, also check `read:project`, `project`, and `gist` as needed.

### 1.4 Generate and copy

1. Click **Generate token (classic)**
2. Copy the token value — it starts with `ghp_` and will not be shown again
3. Do not paste it into any chat, config file, or commit

---

## Phase 2: Store the Token and Configure OpenCode

### 2.1 Set the token in your shell profile

Edit `~/.bashrc`. If a `GITHUB_TOKEN` export already exists, update the value. If not, add it:

```bash
export GITHUB_TOKEN="ghp_your_token_here"
```

Then reload:

```bash
source ~/.bashrc
```

### 2.2 Update the OpenCode config to use the environment variable

Edit `~/.config/opencode/opencode.jsonc`. Find the `github` MCP entry and ensure the `Authorization` header uses the `{env:GITHUB_TOKEN}` syntax:

```jsonc
"github": {
  "enabled": true,
  "type": "remote",
  "url": "https://api.githubcopilot.com/mcp/",
  "headers": {
    "Authorization": "Bearer {env:GITHUB_TOKEN}"
  }
}
```

The `{env:GITHUB_TOKEN}` syntax tells OpenCode to read the `GITHUB_TOKEN` environment variable at startup and inject it into the Authorization header. The token never appears in the config file.

---
## Phase 3: Verify

### 3.1 Restart OpenCode

Kill existing processes and relaunch:

```bash
pkill -f OpenCode
pkill -f opencode-cli
```

Open OpenCode from your desktop application launcher, or run `opencode-cli` for CLI usage.

### 3.2 Verify MCP connection

```bash
opencode-cli mcp list
```

This confirms the GitHub MCP server connects and authenticates successfully.

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `403 Forbidden` on org repos | SAML SSO not authorized | Authorize the token for `Brothertown-Language` (Phase 2.3) |
| `403 Forbidden` on all repos | Token expired or revoked | Create a new token (Phase 1) |
| `401 Unauthorized` | `GITHUB_TOKEN` not set or wrong | Verify `echo $GITHUB_TOKEN` is not empty |
| Works in browser, fails in API | Fine-grained token | Recreate as classic token |
| `gh` CLI works but OpenCode doesn't | Different token source | Ensure `GITHUB_TOKEN` env var is set (OpenCode uses this; `gh` uses its own auth) |
| Notifications tools return 403 | Missing `notifications` scope | Recreate token with `notifications` scope checked |
| Security tools return 403 | Missing `security_events` scope | Recreate token with `security_events` scope checked |