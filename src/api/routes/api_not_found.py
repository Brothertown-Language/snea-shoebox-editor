# SPDX-FileCopyrightText: 2026 Michael Conrad
# SPDX-License-Identifier: MIT
"""JSON 404 catch-all for unknown paths under ``/api/`` (#1420).

Must be evaluated after the specific endpoint rules but before Streamlit's
own catch-all, so unknown API paths never fall through to the UI.
"""

from __future__ import annotations

from ..errors import send_error_json
from . import BaseAPIHandler

PATH = "/api/.*"


class ApiNotFoundHandler(BaseAPIHandler):
    """Any method on an unmatched ``/api/`` path receives the JSON 404."""

    def get(self) -> None:
        send_error_json(self, 404)

    post = get
    put = get
    delete = get
    patch = get


PATH = "/api/.*"
HANDLER = ApiNotFoundHandler
