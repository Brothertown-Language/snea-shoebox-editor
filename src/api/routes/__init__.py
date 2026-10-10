# SPDX-FileCopyrightText: 2026 Michael Conrad
# SPDX-License-Identifier: MIT
"""Per-endpoint route modules for the agent-facing API (#1420).

Each module declares its own path pattern and handler; new endpoints are
added as new modules under this package. :class:`BaseAPIHandler` carries the
shared contract: GET-only surface (405 for other methods, JSON), UTF-8 JSON
responses with unescaped Unicode, and no XSRF checks (header-authenticated
API, not cookie-based).
"""

from __future__ import annotations

import json

import tornado.web

from ..errors import send_error_json


class BaseAPIHandler(tornado.web.RequestHandler):
    """Shared behavior for API route handlers."""

    # Tornado XSRF checks apply to POST/PUT/DELETE/PATCH; the API is
    # authenticated via headers, not cookies, so the check is meaningless
    # here and would replace our JSON 405 with an HTML 403.
    def check_xsrf_cookie(self) -> None:  # noqa: D102 - intentional no-op
        return None

    def send_json(self, payload: dict, status: int = 200) -> None:
        """Write a JSON response: UTF-8, unescaped Unicode (R-10)."""
        self.set_status(status)
        self.set_header("Content-Type", "application/json; charset=utf-8")
        self.write(json.dumps(payload, ensure_ascii=False).encode("utf-8"))

    def _method_not_allowed(self) -> None:
        send_error_json(self, 405)

    post = _method_not_allowed
    put = _method_not_allowed
    delete = _method_not_allowed
    patch = _method_not_allowed
    options = _method_not_allowed
