# SPDX-FileCopyrightText: 2026 Michael Conrad
# SPDX-License-Identifier: MIT
"""JSON error contract for the agent-facing API (#1420, spec Interface Contract).

Every API response carries ``Content-Type: application/json; charset=utf-8``.
Error bodies use the shape::

    {"error": {"code": "<code>", "message": "<generic message>"}}

Messages are static/generic and never include DB connection details, host
names, SQL, or stack traces (SC-12 blocklist).
"""

from __future__ import annotations

import json

# Static, generic messages — never distinguish unknown key from bad secret,
# never name infrastructure. Values are data: no dynamic content is formatted
# into any message.
MESSAGES: dict[int, tuple[str, str]] = {
    401: ("unauthorized", "Authentication required."),
    403: ("key_disabled", "API key is disabled or revoked."),
    404: ("not_found", "Unknown API endpoint."),
    405: ("method_not_allowed", "Method not allowed."),
    429: ("rate_limited", "Rate limit exceeded."),
    503: ("service_unavailable", "Service temporarily unavailable."),
}


def error_body(status: int) -> bytes:
    """Serialize the canonical JSON error body for a status code."""
    code, message = MESSAGES.get(status, ("error", "Request failed."))
    return json.dumps(
        {"error": {"code": code, "message": message}},
        ensure_ascii=False,
    ).encode("utf-8")


def send_error_json(handler, status: int, extra_headers: dict[str, str] | None = None) -> None:
    """Write the canonical JSON error response on a Tornado handler."""
    handler.set_status(status)
    handler.set_header("Content-Type", "application/json; charset=utf-8")
    if extra_headers:
        for name, value in extra_headers.items():
            handler.set_header(name, value)
    handler.write(error_body(status))
