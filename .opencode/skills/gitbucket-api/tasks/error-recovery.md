# GitBucket Error Recovery

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| "Bad credentials" | Basic auth attempted | Use `Authorization: token {TOKEN}` header only |
| "Not Found" | Wrong endpoint URL | Verify path: `/api/v3/repos/{owner}/{repo}/...` |
| "Unauthorized" | Token missing or invalid | Check `GITBUCKET_TOKEN` environment variable |
| 422 Unprocessable Entity | Validation error | Check request body format (array for labels, not objects) |

## Authentication Errors

### "Bad credentials"

**Cause**: Using HTTP Basic authentication instead of token authentication.

**Wrong**:
```python
import base64
credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
headers = {"Authorization": f"Basic {credentials}"}  # ❌ FAILS
```

**Correct**:
```python
token = os.environ.get("GITBUCKET_TOKEN")
headers = {"Authorization": f"token {token}"}  # ✅ WORKS
```

**Explanation**: GitBucket does not support HTTP Basic authentication for API calls. Token authentication is required for all API operations.

### "Unauthorized"

**Cause**: Token missing, empty, or invalid.

**Solution**:
1. Check `GITBUCKET_TOKEN` is set: `echo $GITBUCKET_TOKEN`
2. Verify token has correct scopes
3. Regenerate token in GitBucket UI if corrupted

## Endpoint Errors

### "Not Found"

**Cause**: Incorrect URL format or missing repository.

**Debug steps**:
```python
# Verify URL components
print(f"URL: {GITBUCKET_URL}api/v3/repos/{owner}/{repo}/issues")
print(f"Expected format: /api/v3/repos/:owner/:repo/:endpoint")
```

**Common mistakes**:
- Missing `/gitbucket/` in URL path
- Wrong owner name (case-sensitive)
- Wrong repository name (case-sensitive)

### 422 Unprocessable Entity

**Cause**: Request body format incorrect.

**Example - Labels**:
```python
# WRONG: Object format (GitHub style)
json={"labels": [{"name": "bug"}, {"name": "enhancement"}]}  # ❌

# CORRECT: Array format (GitBucket style)
json=["bug", "enhancement"]  # ✅
```

## Session Init Detection

Session init script (`ai_bin/session_init.py`) detects GitBucket from remote URL and outputs:

```
GIT_PLATFORM=gitbucket
GITBUCKET_HTML_URL=https://gitbucket.example.com/gitbucket/
GITBUCKET_HAS_CREDENTIALS=true
```

**If `GITBUCKET_HAS_CREDENTIALS=false`**, token is missing from `.env`.

## Token Validation

```python
def validate_token():
    """Verify GitBucket token works."""
    response = requests.get(
        f"{GITBUCKET_URL}api/v3/user",
        headers={"Authorization": f"token {GITBUCKET_TOKEN}"}
    )
    if response.status_code == 200:
        print("Token valid")
        return True
    if response.status_code == 401:
        print("Token invalid or expired")
        return False
    if response.status_code == 404:
        print("Wrong endpoint or GitBucket URL")
        return False
```

## Fallback Strategy

If GitBucket API fails:
1. Check authentication (token present and valid)
2. Verify URL format
3. Check repository exists and is accessible
4. Fall back to GitBucket web UI for operations not supported by API