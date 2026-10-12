# SPDX-FileCopyrightText: 2026 Michael Conrad
# SPDX-License-Identifier: MIT
# Provenance: AI-generated (issue #1436)
"""Session-scoped executable API-bolt warmup — issue #1436.

The agent-facing API bolt is installed on the app's FIRST browser script
run.  The full-suite collection (``test/test_api_*``) sorts before
``test/ui/``, and the headless app never auto-connects a browser, so an
``SNEA_E2E=1`` full-suite invocation used to race the unbolted app: every
``/api/*`` request fell through to Streamlit's static catch-all.

This conftest carries a session-scoped autouse fixture that, only when
``SNEA_E2E=1`` is set AND the app answers ``/_stcore/health`` (that gate
precedes any browser or Playwright use), opens one throwaway headless
browser session against the app to trigger the first script run, then waits
until a no-credential probe of the API returns 401 JSON — the
bolt-installed signal — before releasing the suite.  Idempotent by the
registrar's existing latch: an already-bolted app short-circuits without
any browser session.

A warmup that cannot reach a bolted state within its bound fails the
session loudly rather than hanging the suite.
"""

from __future__ import annotations

import os
import threading
import time

import pytest
from api_e2e_gate import api_probe, app_healthy, base_url, probe_is_bolted

WARMUP_TIMEOUT_SECONDS = 90.0
POLL_INTERVAL_SECONDS = 1.0


def _trigger_first_script_run(base: str) -> None:
    """Open one throwaway headless browser session to run the app script.

    Runs in a worker thread per the test/ui harness convention (pytest 9 +
    anyio keeps an asyncio loop on the main thread; the Playwright sync API
    forbids entering under a running loop).
    """
    from playwright.sync_api import sync_playwright

    error: list[BaseException] = []

    def _run() -> None:
        try:
            with sync_playwright() as pw:
                browser = pw.chromium.launch(headless=True)
                try:
                    page = browser.new_page()
                    page.goto(base, wait_until="domcontentloaded", timeout=30_000)
                    # Any script run installs the bolt (login page included);
                    # give the script run a moment to complete its
                    # initialization path before closing.
                    page.wait_for_timeout(3_000)
                finally:
                    browser.close()
        except BaseException as exc:  # noqa: BLE001 — reported, never swallowed
            error.append(exc)

    thread = threading.Thread(target=_run, name="snea-api-bolt-warmup", daemon=True)
    thread.start()
    thread.join(timeout=WARMUP_TIMEOUT_SECONDS / 2)
    if thread.is_alive():
        pytest.fail(
            "API bolt warmup browser session did not finish in time — "
            "the warmup cannot reach the live app at "
            f"{base}. Not hanging the suite.",
            pytrace=False,
        )
    if error:
        pytest.fail(
            f"API bolt warmup browser session failed: {error[0]!r} — "
            "the warmup cannot trigger the first script run at "
            f"{base}.",
            pytrace=False,
        )


@pytest.fixture(scope="session", autouse=True)
def warm_api_bolt():
    """Trigger the first script run and wait for the bolt before the suite."""
    if os.environ.get("SNEA_E2E", "") != "1":
        yield
        return
    base = base_url()
    if not app_healthy(base):
        # No live app: the suites' own health checks skip loudly by design.
        # No browser session is opened.
        yield
        return
    status, body = api_probe(base)
    if probe_is_bolted(status, body):
        yield  # already bolted — idempotent short-circuit, no browser session
        return
    _trigger_first_script_run(base)
    waited = 0.0
    while waited < WARMUP_TIMEOUT_SECONDS:
        status, body = api_probe(base)
        if probe_is_bolted(status, body):
            break
        time.sleep(POLL_INTERVAL_SECONDS)
        waited += POLL_INTERVAL_SECONDS
    else:
        pytest.fail(
            "API bolt warmup did not observe the bolt-installed signal "
            f"(401 JSON from /api/v1/records) within {WARMUP_TIMEOUT_SECONDS:.0f}s "
            f"at {base} — the app answered health but never installed the "
            "API bolt. Failing loudly rather than running the API suites "
            "against the static catch-all.",
            pytrace=False,
        )
    yield
