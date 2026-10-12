# SPDX-FileCopyrightText: 2026 Michael Conrad
# SPDX-License-Identifier: MIT
# Provenance: AI-generated (issue #1436)
"""Shared bolt-presence gate for the live API E2E suites — issue #1436.

The agent-facing API is a Tornado bolt installed on the running server during
the app's FIRST browser script run (``streamlit_app.py`` →
``src/api/registrar.py::install_api_routes``).  If the API tests run before
any browser session exists, every ``/api/*`` request falls through to
Streamlit's static catch-all (``index.html``, HTTP 200 text/html) and the
auth assertions fail with uninterpretable reds.

This module provides:

- ``app_healthy`` — the ``/_stcore/health`` probe shared by the suites.
- ``api_probe`` — a no-credential GET of ``/api/v1/records`` returning
  ``(status, body)``; on a bolted app this is ``401`` with a JSON error body.
- ``require_bolted_api`` — the shared setUpClass gate: fails the class
  loudly, naming the uninstalled bolt and the warmup requirement, whenever
  the no-credential probe response is not 401 JSON.

Importable by test modules directly (``from api_e2e_gate import ...``) —
pytest's default import mode puts ``test/`` on ``sys.path`` — and by
``test/conftest.py`` for the executable warmup.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request


def base_url() -> str:
    return os.environ.get("SNEA_E2E_BASE_URL", "http://localhost:8501")


def app_healthy(base: str | None = None) -> bool:
    """True when the live app answers ``/_stcore/health`` with 200."""
    base = base or base_url()
    try:
        with urllib.request.urlopen(base + "/_stcore/health", timeout=2) as r:
            return r.status == 200
    except (urllib.error.URLError, OSError):
        return False


def api_probe(base: str | None = None) -> tuple[int, bytes]:
    """No-credential GET of the records endpoint.

    Returns ``(status, body)``.  A bolted app answers 401 with a JSON error
    body; an unbolted app serves Streamlit's static catch-all (200 text/html
    ``index.html``, or 405 HTML on POST).
    """
    base = base or base_url()
    req = urllib.request.Request(base + "/api/v1/records", method="GET")
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


def probe_is_bolted(status: int, body: bytes) -> bool:
    """True when the probe response is the bolt-installed signal: 401 JSON."""
    if status != 401:
        return False
    try:
        payload = json.loads(body.decode("utf-8", errors="replace"))
    except (ValueError, UnicodeDecodeError):
        return False
    return isinstance(payload, dict)


def require_bolted_api(base: str | None = None) -> None:
    """setUpClass gate: fail loudly when the API bolt is not installed.

    Called after each live class's existing health check.  Any probe response
    other than 401 JSON — 200 text/html is the unbolted static catch-all —
    fails the class with a message naming the uninstalled bolt and the
    warmup requirement, instead of leaving every auth assertion in the class
    red against catch-all HTML.
    """
    base = base or base_url()
    status, body = api_probe(base)
    if probe_is_bolted(status, body):
        return
    snippet = body[:200].decode("utf-8", errors="replace")
    raise AssertionError(
        "API bolt not installed on the live app at "
        f"{base}: no-credential probe of /api/v1/records returned "
        f"HTTP {status} (expected 401 JSON), body starts: {snippet!r}. "
        "The bolt is installed on the app's FIRST browser script run — "
        "run the Playwright warmup (SNEA_E2E=1 with the live app up; the "
        "test/conftest.py session warmup performs this automatically) "
        "before this suite."
    )
