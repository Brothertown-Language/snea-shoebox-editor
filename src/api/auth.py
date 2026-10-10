# Copyright (c) 2026 Brothertown Language
# <!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
"""Request authentication for the agent-facing API (#1420).

Credential scheme (spec Interface Contract): ``X-API-Key`` identifies the
key, ``X-API-Secret`` authenticates it. Header values are compared exactly
as received — no trimming, no case normalization; empty values fail as
missing.

Status semantics (R-5):

- **401** (uniform message) — missing headers, unknown key, or wrong secret;
  never distinguishes unknown key from bad secret
- **403** — a known key that is disabled or revoked
- **503** — database unavailable (fail closed)

Every failed attempt (401 and 403) is audited as ``api_auth_failure`` (R-13)
with the presented key identifier (if parseable), the outcome, and the
client address — never the presented secret.
"""

from __future__ import annotations

import threading
import time

from src.logging_config import get_logger

from .context import get_rate_limit, get_session_factory
from .errors import send_error_json

logger = get_logger("src.api.auth")

KEY_HEADER = "X-API-Key"
SECRET_HEADER = "X-API-Secret"

_WINDOW_SECONDS = 60.0


class _RateLimiter:
    """In-memory per-process fixed-window limiter, keyed by API key (R-14).

    Only VALIDATED keys reach the limiter (checked after successful
    authentication), so the key set is bounded by admin-issued keys.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._windows: dict[str, tuple[float, int]] = {}  # key -> (window_start, count)

    def check(self, key: str) -> int | None:
        """Count one request for `key`; return Retry-After seconds when limited."""
        limit = get_rate_limit()
        now = time.monotonic()
        window_start = now - (now % _WINDOW_SECONDS)
        with self._lock:
            start, count = self._windows.get(key, (window_start, 0))
            if start != window_start:
                start, count = window_start, 0
            count += 1
            if count > limit:
                retry_after = int(start + _WINDOW_SECONDS - now) + 1
                return max(retry_after, 1)
            self._windows[key] = (start, count)
            return None


limiter = _RateLimiter()


def _log_auth_failure(outcome: str, presented_key: str | None, remote_ip: str) -> None:
    """Audit a failed authentication attempt (R-13). Never logs the secret."""
    try:
        from src.services.event_log_service import EventLogService

        EventLogService.log_event(
            event_type="api_auth_failure",
            severity="warning",
            message=f"API authentication failed ({outcome})",
            source="src.api.auth",
            details={
                "outcome": outcome,
                "presented_key": presented_key,
                "client_address": remote_ip,
            },
        )
    except Exception:
        logger.error("Failed to persist api_auth_failure event", exc_info=True)


def require_credentials(handler) -> bool:
    """Authenticate the request; on failure, emit the JSON error response.

    Returns True when the credential pair is valid and active; False after
    writing the uniform 401 or the 403 (handlers simply
    ``if not require_credentials(self): return``).
    """
    key = handler.request.headers.get(KEY_HEADER, "")
    secret = handler.request.headers.get(SECRET_HEADER, "")
    remote_ip = handler.request.remote_ip

    if not key or not secret:
        _log_auth_failure("missing_headers" if not key and not secret else "missing_header", key or None, remote_ip)
        send_error_json(handler, 401)
        return False

    factory = get_session_factory()
    if factory is None:
        # Bolt captured no session factory — the API cannot authenticate.
        logger.error("No session factory captured at bolt time; failing closed")
        send_error_json(handler, 503)
        return False

    try:
        from src.services.api_key_service import ApiKeyService

        status, _row = ApiKeyService.authenticate(key, secret)
    except Exception:
        logger.error("Auth lookup failed (database unavailable); failing closed", exc_info=True)
        send_error_json(handler, 503)
        return False

    if status == "ok":
        retry_after = limiter.check(key)
        if retry_after is not None:
            send_error_json(handler, 429, extra_headers={"Retry-After": str(retry_after)})
            return False
        return True
    if status == "inactive":
        _log_auth_failure("key_inactive", key, remote_ip)
        send_error_json(handler, 403)
        return False
    # "invalid" — unknown key or wrong secret: one uniform 401 (R-5)
    _log_auth_failure("invalid_credentials", key, remote_ip)
    send_error_json(handler, 401)
    return False
