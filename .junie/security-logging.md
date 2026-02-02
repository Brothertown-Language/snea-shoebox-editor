---
author: Human
contributor: AI
status: active
date: 2026-02-01
---
<!-- Copyright (c) 2026 Brothertown Language -->

# Security: Logging and Error Handling

## Safe logging practices

### NEVER log sensitive data

**Prohibited in logs:**
- Tokens, passwords, API keys
- Session IDs, authentication cookies
- Personally Identifiable Information (PII)
- Credit card numbers, SSNs
- Internal system paths (in production)
- Database connection strings with credentials

### Sanitize user input before logging

**Always sanitize:**
```python
import logging
from typing import Any

def sanitize_for_log(value: Any) -> str:
    """Sanitize value for safe logging."""
    if isinstance(value, str):
        # Remove potential sensitive patterns
        sanitized = value
        if 'token' in value.lower() or 'key' in value.lower():
            return '[REDACTED]'
        # Truncate long values
        if len(sanitized) > 200:
            return sanitized[:200] + '...'
        return sanitized
    return str(value)

# Usage
logging.info(f"Processing request: {sanitize_for_log(user_input)}")
```

### Use appropriate log levels

**Log level guidelines:**
- **DEBUG** - Detailed diagnostic information (development only)
  - Variable values, function entry/exit
  - Never enabled in production
- **INFO** - General informational messages
  - Request received, operation completed
  - User actions (sanitized)
- **WARNING** - Warning messages for recoverable issues
  - Deprecated API usage, fallback behavior
  - Rate limit approaching
- **ERROR** - Error messages for failures
  - Exception caught and handled
  - Operation failed but application continues
- **CRITICAL** - Critical issues requiring immediate attention
  - System failure, data corruption
  - Security breach detected

### Cloudflare Workers logging

**Be aware:**
- Logs are visible in Cloudflare dashboard
- Logs may be retained for compliance/debugging
- Never log secrets even in development
- Use structured logging for easier filtering

Example:
```python
import json
from typing import Dict, Any

def log_structured(level: str, message: str, context: Dict[str, Any]) -> None:
    """Log structured data safely."""
    # Sanitize context
    safe_context = {
        k: '[REDACTED]' if any(s in k.lower() for s in ['token', 'key', 'password']) else v
        for k, v in context.items()
    }
    
    log_entry = {
        'level': level,
        'message': message,
        'context': safe_context
    }
    print(json.dumps(log_entry))
```

## Error handling

### NEVER expose internal details to users

**Bad - exposes internals:**
```python
except Exception as e:
    return {"error": str(e)}  # May expose paths, SQL, etc.
```

**Good - generic user message:**
```python
import logging
from typing import Dict, Any

def handle_error(e: Exception, user_message: str) -> Dict[str, Any]:
    """Handle error with safe user message and detailed logging."""
    # Log detailed error for developers
    logging.error(f"Operation failed: {type(e).__name__}: {str(e)}", exc_info=True)
    
    # Return generic message to user
    return {
        "error": user_message,
        "success": False
    }

# Usage
try:
    result = dangerous_operation()
except Exception as e:
    return handle_error(e, "An error occurred. Please try again.")
```

### Error message guidelines

**For users:**
- Generic, helpful messages
- No stack traces or internal paths
- Actionable guidance when possible
- Examples:
  - "An error occurred. Please try again."
  - "Invalid input. Please check your data and try again."
  - "Unable to save changes. Please contact support if this persists."

**For developers (in logs):**
- Include exception type and message
- Include stack trace (use `exc_info=True`)
- Include relevant context (sanitized)
- Include request ID for tracing

### Validation errors

**Provide helpful feedback without exposing internals:**

```python
from typing import List, Dict, Any

def validate_mdf_entry(entry: str) -> Dict[str, Any]:
    """Validate MDF entry and return user-friendly errors."""
    errors: List[str] = []
    
    if not entry.strip():
        errors.append("Entry cannot be empty")
    
    if not entry.startswith('\\'):
        errors.append("Entry must start with a marker (e.g., \\lx)")
    
    # Don't expose: file paths, line numbers, internal validation logic
    if errors:
        return {
            "valid": False,
            "errors": errors,
            "message": "Please correct the following issues:"
        }
    
    return {"valid": True}
```

## Security event logging

### Log security-relevant events

**Always log:**
- Authentication attempts (success and failure)
- Authorization failures
- Input validation failures
- Rate limit violations
- Suspicious patterns (SQL injection attempts, path traversal)

**Example:**
```python
import logging
from typing import Optional

def log_security_event(
    event_type: str,
    user_id: Optional[str],
    details: str,
    severity: str = 'WARNING'
) -> None:
    """Log security-relevant events."""
    log_func = getattr(logging, severity.lower())
    log_func(
        f"SECURITY: {event_type} | "
        f"User: {user_id or 'anonymous'} | "
        f"Details: {details}"
    )

# Usage
log_security_event(
    'AUTH_FAILURE',
    user_id='user123',
    details='Invalid password attempt',
    severity='WARNING'
)
```

### Don't log successful authentication credentials

**Bad:**
```python
logging.info(f"User {username} logged in with password {password}")
```

**Good:**
```python
logging.info(f"User {username} logged in successfully")
```
