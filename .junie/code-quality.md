---
author: Human
contributor: AI
status: active
date: 2026-02-01
---
<!-- Copyright (c) 2026 Brothertown Language -->

# Code Quality and Safety Standards

## Pre-commit checklist

### Before every commit

Run through this checklist:

- [ ] **No sensitive data** in code or comments
  - No API keys, tokens, passwords
  - No email addresses or PII
  - No internal URLs or system paths
- [ ] **No sensitive files staged**
  - Verified with `git status`
  - No `.env`, `secrets.toml`, or `credentials` files
  - Use `git check-ignore` if unsure
- [ ] **All new functions have type annotations**
  - Parameters typed
  - Return values typed
  - No `Any` types unless unavoidable
- [ ] **Tests added/updated for changes**
  - Bug fixes have reproduction tests
  - New features have appropriate test coverage
  - Refactorings verified by existing tests
- [ ] **No hardcoded configuration**
  - No hardcoded URLs, paths, or credentials
  - Use environment variables or configuration files
- [ ] **Copyright headers present on new files**
  - Python files: `# Copyright (c) 2026 Brothertown Language`
  - Markdown files: `<!-- Copyright (c) 2026 Brothertown Language -->`
- [ ] **Commit message created**
  - File: `tmp/commit.msg`
  - Plain descriptive text (no Conventional Commits prefixes)
  - Remove `tmp/commit.msg` after committing

### Verification commands

```bash
# Check what will be committed
git status

# Review changes for secrets
git diff --cached | grep -iE "token|key|secret|password|api_key"

# Verify no ignored files are staged
git status --short | grep -E "^[AM].*" | cut -c 4- | xargs -I {} git check-ignore -v {}
```

## Code quality standards

### No commented-out code

**Bad:**
```python
def process_data(data: str) -> str:
    # old_result = legacy_process(data)
    # return old_result
    return new_process(data)
```

**Good:**
```python
def process_data(data: str) -> str:
    """Process data using new algorithm."""
    return new_process(data)
```

**Rationale:** Use git history instead of commented code. If you need to reference old code, include a commit hash in a comment.

### No debug print statements

**Bad:**
```python
def calculate_total(items: List[Item]) -> float:
    print(f"DEBUG: items = {items}")
    total = sum(item.price for item in items)
    print(f"DEBUG: total = {total}")
    return total
```

**Good:**
```python
import logging
from typing import List

def calculate_total(items: List[Item]) -> float:
    """Calculate total price of items."""
    logging.debug(f"Calculating total for {len(items)} items")
    total = sum(item.price for item in items)
    logging.debug(f"Total calculated: {total}")
    return total
```

**Rationale:** Use proper logging with appropriate levels. Debug prints can leak sensitive data and clutter production logs.

### TODO comments require tracking

**Bad:**
```python
# TODO: fix this later
def broken_function():
    pass
```

**Good:**
```python
# TODO(issue-123): Implement proper error handling for edge case
# See: https://github.com/org/repo/issues/123
def needs_improvement():
    pass
```

**Rationale:** TODOs without context or tracking get forgotten. Link to issues or document why it's deferred.

### Consistent formatting

**Follow existing codebase style:**
- Match indentation (spaces vs tabs, indent size)
- Match naming conventions (snake_case, camelCase, etc.)
- Match import order and grouping
- Match comment frequency and style
- Use same language as existing comments

**When in doubt:**
```bash
# Check existing style in similar files
grep -A 5 "def " src/backend/*.py | head -20
```

## Input validation

### ALWAYS validate user input

**Validation checklist:**
- [ ] Type checking (is it the expected type?)
- [ ] Range checking (is it within valid bounds?)
- [ ] Format checking (does it match expected pattern?)
- [ ] Length checking (is it reasonable length?)
- [ ] Sanitization (remove/escape dangerous characters?)

### Example validation

```python
from typing import Optional, Dict, Any, List
import re

def validate_lexeme(lexeme: str) -> Dict[str, Any]:
    """Validate MDF lexeme entry."""
    errors: List[str] = []
    
    # Type check (already done by type annotation)
    if not isinstance(lexeme, str):
        return {"valid": False, "errors": ["Lexeme must be a string"]}
    
    # Length check
    if len(lexeme) > 1000:
        errors.append("Lexeme too long (max 1000 characters)")
    
    if len(lexeme.strip()) == 0:
        errors.append("Lexeme cannot be empty")
    
    # Format check
    if not lexeme.startswith('\\lx '):
        errors.append("Lexeme must start with \\lx marker")
    
    # Sanitization check (no control characters)
    if re.search(r'[\x00-\x08\x0B\x0C\x0E-\x1F]', lexeme):
        errors.append("Lexeme contains invalid control characters")
    
    if errors:
        return {
            "valid": False,
            "errors": errors,
            "message": "Validation failed"
        }
    
    return {"valid": True}
```

### Sanitize before database operations

**Use parameterized queries:**
```python
from typing import Any

# Good - parameterized (D1 binding handles this)
async def save_entry(db: Any, lexeme: str, gloss: str) -> None:
    """Save entry to database safely."""
    await db.prepare(
        "INSERT INTO entries (lexeme, gloss) VALUES (?, ?)"
    ).bind(lexeme, gloss).run()

# Bad - string concatenation (SQL injection risk)
async def save_entry_bad(db: Any, lexeme: str, gloss: str) -> None:
    """UNSAFE: SQL injection vulnerability."""
    query = f"INSERT INTO entries (lexeme, gloss) VALUES ('{lexeme}', '{gloss}')"
    await db.exec(query)
```

### Validate before processing

**Fail fast with clear errors:**
```python
from typing import Dict, Any

def process_mdf_entry(entry: str) -> Dict[str, Any]:
    """Process MDF entry with validation."""
    # Validate first
    validation = validate_lexeme(entry)
    if not validation["valid"]:
        return {
            "success": False,
            "error": "Invalid entry",
            "details": validation["errors"]
        }
    
    # Process only if valid
    result = parse_and_save(entry)
    return {"success": True, "result": result}
```

## Database safety

### Use parameterized queries

**Always use parameter binding:**
- Prevents SQL injection
- Handles escaping automatically
- More readable and maintainable

**D1 binding example:**
```python
from typing import Any, Optional

async def get_entry_by_id(db: Any, entry_id: int) -> Optional[Dict[str, Any]]:
    """Get entry by ID safely."""
    result = await db.prepare(
        "SELECT * FROM entries WHERE id = ?"
    ).bind(entry_id).first()
    
    return result
```

### Validate data before INSERT/UPDATE

**Check constraints before database operation:**
```python
from typing import Dict, Any

async def update_entry(
    db: Any,
    entry_id: int,
    lexeme: str,
    version: int
) -> Dict[str, Any]:
    """Update entry with optimistic locking."""
    # Validate input
    if not lexeme or len(lexeme) > 1000:
        return {"success": False, "error": "Invalid lexeme"}
    
    # Optimistic locking check
    result = await db.prepare(
        "UPDATE entries SET lexeme = ?, version = version + 1 "
        "WHERE id = ? AND version = ?"
    ).bind(lexeme, entry_id, version).run()
    
    if result.meta.changes == 0:
        return {"success": False, "error": "Version conflict"}
    
    return {"success": True}
```

### Optimistic locking

**Already implemented with version tracking:**
- Each record has a `version` field
- UPDATE checks current version matches expected version
- Prevents lost updates in concurrent edits
- Returns error if version mismatch detected

## API security

### Input validation for all endpoints

**Validate every API parameter:**
```python
from typing import Any, Dict

async def api_update_entry(request: Any) -> Dict[str, Any]:
    """API endpoint with validation."""
    # Parse request
    try:
        data = await request.json()
    except Exception:
        return {"error": "Invalid JSON"}, 400
    
    # Validate required fields
    if "id" not in data or "lexeme" not in data:
        return {"error": "Missing required fields"}, 400
    
    # Validate types
    if not isinstance(data["id"], int):
        return {"error": "ID must be integer"}, 400
    
    if not isinstance(data["lexeme"], str):
        return {"error": "Lexeme must be string"}, 400
    
    # Validate values
    validation = validate_lexeme(data["lexeme"])
    if not validation["valid"]:
        return {"error": validation["errors"]}, 400
    
    # Process request
    result = await update_entry(db, data["id"], data["lexeme"], data["version"])
    return result
```

### Authentication and authorization

**For production deployment:**
- Implement authentication (OAuth, API keys, etc.)
- Validate user permissions before operations
- Log authentication attempts
- Rate limit to prevent abuse

**Placeholder for future implementation:**
```python
from typing import Optional, Any

def authenticate_request(request: Any) -> Optional[str]:
    """Authenticate request and return user ID."""
    # TODO: Implement authentication
    # - Check Authorization header
    # - Validate token/session
    # - Return user ID or None
    return None

def authorize_operation(user_id: str, operation: str, resource_id: int) -> bool:
    """Check if user is authorized for operation."""
    # TODO: Implement authorization
    # - Check user permissions
    # - Verify resource ownership
    # - Return True if authorized
    return False
```

### CORS configuration

**Configure for frontend origin:**
```python
from typing import Dict

def get_cors_headers(origin: str) -> Dict[str, str]:
    """Get CORS headers for response."""
    allowed_origins = [
        "https://snea-shoebox-editor.pages.dev",
        "http://localhost:8000",  # Local development
    ]
    
    if origin in allowed_origins:
        return {
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
        }
    
    return {}
```

### Rate limiting

**Consider for public-facing endpoints:**
```python
from typing import Dict, Any
from datetime import datetime, timedelta

# Simple in-memory rate limiter (use Redis/KV for production)
rate_limit_store: Dict[str, Any] = {}

def check_rate_limit(client_id: str, max_requests: int = 100, window_seconds: int = 60) -> bool:
    """Check if client has exceeded rate limit."""
    now = datetime.now()
    
    if client_id not in rate_limit_store:
        rate_limit_store[client_id] = {"count": 1, "reset": now + timedelta(seconds=window_seconds)}
        return True
    
    client_data = rate_limit_store[client_id]
    
    if now > client_data["reset"]:
        # Reset window
        rate_limit_store[client_id] = {"count": 1, "reset": now + timedelta(seconds=window_seconds)}
        return True
    
    if client_data["count"] >= max_requests:
        return False
    
    client_data["count"] += 1
    return True
```
