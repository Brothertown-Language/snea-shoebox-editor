# HTTP Requests

## HTTP Headers — Always Include

When making HTTP requests (via `urllib.request`, `requests`, `httpx`, or any HTTP client), always include a complete set of modern browser-like headers to avoid being blocked or served error pages.

### Required Headers

```python
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "application/xml,application/xhtml+xml,text/html;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
}
```

### Rationale

- **User-Agent**: Many servers (including NLM, NIH, PubMed) reject or throttle requests without a browser-like User-Agent. Custom agent strings like `my-app/1.0` are often blocked or served HTML error pages instead of content.
- **Accept**: Signals content type preferences. Critical for API endpoints that serve multiple formats.
- **Accept-Language**: Some endpoints return localized error pages if this is missing.
- **Accept-Encoding**: Enables compression support in the response.

### Anti-Patterns

```python
# WRONG: Minimal or custom User-Agent
urllib.request.Request(url, headers={"User-Agent": "my-crawler/1.0"})

# WRONG: No headers
urllib.request.urlopen(url)

# WRONG: Incomplete headers
headers = {"User-Agent": "Mozilla/5.0"}  # Missing Accept, Accept-Language
```

### Correct Pattern

```python
# CORRECT: Full browser-like headers
request = urllib.request.Request(
    url,
    headers={
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/xml,application/xhtml+xml,text/html;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
    },
)
```

## Host and Referrer

For requests where origin validation matters (APIs, protected resources, some CDNs):

- **Host**: Automatically set by `urllib` from the URL — do not manually set unless you need to override.
- **Referrer**: Set to the base URL of the site or a plausible navigation origin when required by the endpoint:

```python
headers["Referer"] = "https://example.com/"  # Plausible navigation origin
```

## Validation After Download

Always validate downloaded content:

1. **Check file content type** — ensure it's the expected format (XML, JSON, etc.)
2. **Not HTML error page** — servers often return HTTP 200 with HTML error pages instead of proper error codes
3. **Not empty or truncated** — verify file size or content structure

```python
def _is_valid_xml(path: Path) -> bool:
    try:
        content = path.read_text(errors="ignore")
        return content.lstrip().startswith("<?xml") or content.lstrip().startswith("<!DOCTYPE")
    except Exception:
        return False
```

## File Integrity

When re-downloading, check existing files:

- **Existence check alone is insufficient** — files may be corrupted, incomplete, or HTML error pages
- **Validate content format** before skipping download
- **Support force-redownload** via a `force` parameter

```python
need_download = (
    force 
    or not dest_path.exists() 
    or not _is_valid_xml(dest_path)
)
```