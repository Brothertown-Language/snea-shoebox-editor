# Runbook: GitHub PAT Setup for OpenCode GitHub MCP Plugin

> **Audience**: Any team member who needs to configure the OpenCode GitHub MCP plugin on their workstation.
> **Prerequisites**: A GitHub account with access to the Brothertown-Language organization.

## Background

The opencode GitHub MCP plugin authenticates via a GitHub Personal Access Token (PAT). This token must be a **classic** PAT — fine-grained tokens will not work because:

| Limitation | Impact |
|---|---|
| Scopes to a **single resource owner** | Cannot access repos across multiple orgs/users |
| Cannot contribute to **public repos** where you're not a member | Cross-org contributions fail |
| Cannot access repos as an **outside collaborator** | External org repos reject the token |
| Cannot access **Packages** | Package registry operations fail |
| Cannot call the **Checks API** | CI status lookups fail |

If you see `403 Forbidden` errors on repos you can access in the browser, you likely have a fine-grained token. Switch to classic.

---

## Step 1: Create a Classic PAT on GitHub

1. Go to **https://github.com/settings/tokens/new** (classic)
   - Alternatively: Profile picture → Settings → Developer settings → Personal access tokens → Tokens (classic) → Generate new token (classic)

2. Fill in:
   - **Note**: `opencode-github-mcp`
   - **Expiration**: 90 days (recommended). Set a calendar reminder to rotate.

3. Select these scopes:

   | Scope | Why |
   |---|---|
   | `repo` | Full access to code, issues, PRs, commits across all repos you can access |
   | `workflow` | Update GitHub Actions workflow files (needed if opencode modifies CI) |
   | `admin:repo_hook` | Create/manage webhooks |
   | `read:org` | List organization membership, team info |
   | `read:user` | Read user profile data |
   | `user:email` | Access email addresses |
   | `project` | Read/write organization projects |
   | `gist` | Create/delete gists |
   | `write:discussion` | Write discussions |
   | `write:packages` | Upload packages to GitHub Packages |
   | `manage_runners:org` | Manage self-hosted runners (if applicable) |
   | `read:network_configurations` | Read network config (included with `repo` scope) |

4. Click **Generate token** → copy the token immediately (it's shown only once).

5. **If your organization uses SAML SSO**: Click **"Enable SSO"** next to the token → authorize each organization you need access to. Without this step, the token will get `403` on SSO-protected org repos.

---

## Step 2: Store the Token Securely

### Shell Profile

Add to `~/.bashrc` (or `~/.zshrc` for zsh users):

```bash
# GitHub MCP token for opencode
export GITHUB_TOKEN="ghp_your_token_here"
```

Then reload:

```bash
source ~/.bashrc  # or: source ~/.zshrc
```

**Pros**: Available to all tools (git, gh CLI, opencode), survives restarts, easy to rotate.

### What NOT to Do

| Don't | Why |
|---|---|
| Hard-code in `opencode.jsonc` | Plaintext in a config file, easy to leak |
| Commit to git | Even private repos can leak via logs, PRs, stash |
| Share the same token across machines | Compromise on one = compromise on all |
| Use a fine-grained PAT | Won't work across orgs/repos (see Background) |

---

## Step 3: Configure OpenCode

The project-level config is at `.opencode/opencode.jsonc` (checked into the repo). It already references environment variables for local plugins — the GitHub MCP section should go in your **user-level** config.

### User-Level Config: `~/.config/opencode/opencode.jsonc`

Create or edit:

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "github": {
      "enabled": true,
      "type": "remote",
      "url": "https://api.githubcopilot.com/mcp/",
      "headers": {
        "Authorization": "Bearer {env:GITHUB_TOKEN}"
      }
    }
  }
}
```

**Key**: The `{env:GITHUB_TOKEN}` syntax tells opencode to read the `GITHUB_TOKEN` environment variable at startup. This keeps the token out of the config file entirely.

### Merging Behavior

OpenCode merges configs in this order (later overrides earlier):

1. `.opencode/opencode.jsonc` (project-level, checked in)
2.     `$HOME/.opencode/opencode.jsonc` (user-level)

The project config already defines `the-notebook-mcp` and `srclight`. The user config only needs the `github` MCP entry — OpenCode merges them.

---

## Step 4: Verify It Works

```bash
# 1. Confirm the token is available
echo "GITHUB_TOKEN is set: ${GITHUB_TOKEN:+yes}" 
# Should print: GITHUB_TOKEN is set: yes

# 2. Test the token against GitHub API
curl -s -H "Authorization: Bearer $GITHUB_TOKEN" https://api.github.com/user | head -5
# Should return your GitHub profile JSON (not "Bad credentials")

# 3. Test token scopes
curl -sI -H "Authorization: Bearer $GITHUB_TOKEN" https://api.github.com/user | grep x-oauth-scopes
# Should list: repo, workflow, admin:repo_hook, read:org, etc.
```

Then start opencode and confirm the GitHub MCP plugin can list repos, create issues, etc.

---

## Step 5: Token Rotation

Tokens expire. Set a calendar reminder for your chosen expiration date.

### Rotation Checklist

1. Create a new token at https://github.com/settings/tokens (follow Steps 1-2 above)
2. Update the stored token:
   - **Shell profile**: Edit `~/.bashrc` or `~/.zshrc` → change `GITHUB_TOKEN=...` → `source ~/.bashrc`
3. Delete the old token at https://github.com/settings/tokens (classic)
4. Verify with `curl -sI -H "Authorization: Bearer $GITHUB_TOKEN" https://api.github.com/user | grep x-oauth-scopes`

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `403 Forbidden` on org repos | SAML SSO not authorized | Click "Enable SSO" next to the token → authorize the org |
| `403 Forbidden` on all repos | Token expired or revoked | Create a new token |
| `401 Unauthorized` | Token not set or wrong | Verify `echo $GITHUB_TOKEN` is not empty |
| Works in browser, fails in API | Fine-grained token | Recreate as classic token (see Background) |
| `gh` CLI works but opencode doesn't | Different token source | Ensure `GITHUB_TOKEN` env var is set (opencode uses this, `gh` uses its own auth) |
| Token works but can't push workflow files | Missing `workflow` scope | Recreate token with `workflow` scope checked |
| Can't see org projects | Missing `project` scope | Recreate token with `project` scope checked |

---

## Quick Reference Card

```
Token type:    Classic PAT (NOT fine-grained)
Create at:     https://github.com/settings/tokens/new
Scopes:        repo, workflow, admin:repo_hook, read:org,
               read:user, user:email, project, gist,
               write:discussion, write:packages,
               manage_runners:org
Store as:      export GITHUB_TOKEN="ghp_..." in ~/.bashrc
Config:        ~/.config/opencode/opencode.jsonc → "Authorization": "Bearer {env:GITHUB_TOKEN}"
Verify:        curl -sI -H "Authorization: Bearer $GITHUB_TOKEN" https://api.github.com/user | grep x-oauth-scopes
Rotate:        90-day calendar reminder → new token → update env var → delete old token
```

---

*Related: [Credential Leakage Remediation Guide](security/credential-leakage-remediation.md) | [Issue #1052](https://github.com/Brothertown-Language/snea-shoebox-editor/issues/1052)*