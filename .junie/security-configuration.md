---
author: Human
contributor: AI
status: active
date: 2026-02-01
---
<!-- Copyright (c) 2026 Brothertown Language -->

# Security: Configuration Management

## Configuration files

### wrangler.toml

**MUST NOT contain secrets:**
- Never put API tokens, passwords, or keys in `wrangler.toml`
- Use `wrangler secret put` for sensitive values instead
- Safe to commit to repository when secrets are externalized

**Example - Safe wrangler.toml:**
```toml
name = "snea-shoebox-editor"
main = "src/backend/worker.py"
compatibility_date = "2024-01-01"

[[d1_databases]]
binding = "DB"
database_name = "snea_shoebox"
database_id = "your-database-id"  # Not sensitive

# NO secrets here - use wrangler secret put instead
```

**If wrangler.toml contains secrets:**
1. Create `wrangler.toml.example` with dummy values
2. Add `wrangler.toml` to `.gitignore`
3. Document required secrets in README
4. Migrate secrets to Cloudflare secrets or environment variables

### pyproject.toml

**Pin production dependencies:**
```toml
[project]
name = "snea-shoebox-editor"
version = "0.1.0"
dependencies = [
    "streamlit==1.28.0",  # Exact version for production
    "httpx==0.25.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",  # Allow compatible updates for dev
    "black>=23.0.0",
]
```

**Guidelines:**
- Pin exact versions for production dependencies (use `==`)
- Allow version ranges for dev dependencies (use `>=`)
- Document why specific versions are pinned (if non-obvious)
- Update regularly for security patches

### .env and .env.example

**.env (never committed):**
```bash
# Local development secrets
CF_API_TOKEN=your-actual-token-here
GH_TOKEN=your-github-token-here
DATABASE_URL=sqlite:///local.db
```

**.env.example (committed to repository):**
```bash
# Required environment variables for local development
# Copy to .env and fill in actual values

CF_API_TOKEN=your-cloudflare-api-token
GH_TOKEN=your-github-token
DATABASE_URL=sqlite:///local.db
```

**Rules:**
- `.env` MUST be in `.gitignore`
- `.env.example` provides template with dummy values
- Document what each variable is for
- Never commit actual secrets to `.env.example`

## Cloudflare secrets

### Using Cloudflare secrets

**For production secrets:**
```bash
# Set a secret
wrangler secret put SECRET_NAME

# List secrets (shows names only, not values)
wrangler secret list

# Delete a secret
wrangler secret delete SECRET_NAME
```

**In worker code:**
```python
from typing import Any

class Env:
    """Environment bindings for Cloudflare Worker."""
    DB: Any  # D1 database binding
    SECRET_NAME: str  # Secret from wrangler secret put

async def on_fetch(request: Any, env: Env) -> Any:
    """Handle request with access to secrets."""
    secret_value = env.SECRET_NAME
    # Use secret_value safely
    pass
```

### Secret rotation

**When rotating secrets:**
1. Generate new secret value
2. Update in Cloudflare: `wrangler secret put SECRET_NAME`
3. Test that application works with new secret
4. Revoke old secret in external service
5. Document rotation date

**Rotation schedule:**
- API tokens: Every 90 days or when compromised
- Database credentials: Every 180 days or when team member leaves
- Encryption keys: Annually or when compromised

### Bootstrap script secrets

**bootstrap_env.py requirements:**
- `CF_API_TOKEN` - Cloudflare API token with appropriate permissions
- `GH_TOKEN` - GitHub token for repository access

**Setting up:**
```bash
# Export tokens for bootstrap
export CF_API_TOKEN="your-cloudflare-token"
export GH_TOKEN="your-github-token"

# Run bootstrap
uv run python bootstrap_env.py
```

**After bootstrap:**
- Tokens are used to configure Cloudflare resources
- Not stored in repository
- Can be removed from environment after setup

## Environment-specific configuration

### Local development

**Configuration:**
- Use `.env` file for secrets
- Use local SQLite database
- Use `dist/index.html` for frontend (stlite)
- No Cloudflare services required

**Setup:**
```bash
# Create .env from template
cp .env.example .env
# Edit .env with actual values

# Install dependencies
uv pip install -e .

# Build frontend
uv run python scripts/bundle_stlite.py

# Open dist/index.html in browser
```

### Production deployment

**Configuration:**
- Secrets via `wrangler secret put`
- Cloudflare D1 database
- Cloudflare Workers for backend
- Cloudflare Pages for frontend (via Workers)

**Deployment:**
```bash
# Set production secrets (one-time)
wrangler secret put CF_API_TOKEN
wrangler secret put DATABASE_ENCRYPTION_KEY

# Deploy (automatic via git push to main)
git push origin main
```

## Configuration validation

### Startup checks

**Validate configuration at startup:**
```python
import os
from typing import List

def validate_config() -> None:
    """Validate required configuration is present."""
    required_vars: List[str] = [
        'CF_API_TOKEN',
        'DATABASE_URL',
    ]
    
    missing: List[str] = [
        var for var in required_vars 
        if not os.getenv(var)
    ]
    
    if missing:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing)}\n"
            f"See .env.example for required configuration."
        )

# Call at application startup
validate_config()
```

### Configuration documentation

**Document in README:**
- Required environment variables
- Where to get credentials (API tokens, etc.)
- How to set up local development
- How to deploy to production
- Secret rotation procedures

**Keep updated:**
- Update when adding new configuration
- Update when changing deployment process
- Update when rotating secrets
