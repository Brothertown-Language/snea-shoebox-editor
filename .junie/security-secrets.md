---
author: Human
contributor: AI
status: active
date: 2026-02-01
---
<!-- Copyright (c) 2026 Brothertown Language -->

# Security: Secrets Management

## NEVER commit sensitive files

### Critical Rules
- **ZERO TOLERANCE:** **NEVER** commit `.env`, `secrets.toml`, or any file containing credentials, even if you are testing or troubleshooting.
- **NEVER** commit anything in the `.streamlit/` folder. This folder is **STRICTLY IGNORED** and contains sensitive configuration.
- **NEVER** use `git add` on files listed in `.gitignore`.
- **NEVER** use wildcards like `git add .` if there is a risk of staging ignored sensitive files that were untracked.
- **MANDATORY CHECK:** Always run `git status` before committing to verify no ignored files are staged.

### Pre-commit verification
**Before committing:**
1. Run `git status` to see what is staged.
2. Run `git diff --cached` to inspect the content of staged changes for secrets.
3. If a sensitive file is accidentally staged, run `git reset <file>` immediately.

**If accidentally committed:**
1. Use `git rm --cached <file>` immediately
2. Force-push (coordinate with team)
3. Rotate any exposed secrets immediately

## Pre-commit content verification

### ALWAYS check diffs before committing
```bash
git diff --cached
```

### Look for sensitive patterns
Search for these patterns in your diffs:
- `token`
- `key`
- `secret`
- `password`
- `api_key`
- Email addresses
- Internal URLs
- API endpoints with credentials

### If sensitive data found
1. Remove from code immediately
2. Add to .env file
3. Reference via environment variables
4. Update .gitignore if needed
5. Document required variables in README or .env.example

## Environment variables

### NEVER hardcode secrets
- **NEVER hardcode** secrets, tokens, or API keys in source code
- **ALWAYS use** environment variables or Cloudflare secrets
- **Document required variables** in README or .env.example

### Bootstrap requirements
The `bootstrap_env.py` script requires:
- `CF_API_TOKEN` - Cloudflare API token
- `GH_TOKEN` - GitHub token

### Local development
- Use `.env` file (never committed, already in .gitignore)
- Provide `.env.example` with dummy values (committed to repository)
- Load environment variables at application startup

### Production secrets
- Use Cloudflare secrets: `wrangler secret put SECRET_NAME`
- Never store secrets in `wrangler.toml`
- Document secret rotation procedures
