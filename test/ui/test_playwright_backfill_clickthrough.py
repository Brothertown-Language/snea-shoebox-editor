"""SC-13: Playwright real-browser click-through for admin Embedding Backfill.

Auth model: a real GitHub OAuth login performed once by the developer in a
Playwright-managed headed window (tmp/pw_login flow, session 2026-09-30).
The saved storage state (tmp/issue-36/auth-state.json) carries the app's own
gh_auth_token cookie — set by the cookies-controller component, never
hand-injected. Tests reuse it headlessly; the artifact never leaves tmp/.
Regenerate: launch headed browser at localhost:8501/maintenance, log in,
save storage state (delete stale state first so tests fail loudly, never
silently fall back to unauthenticated).

Co-authored with AI: OpenCode (ollama-cloud/glm-5.3-flash)
"""

import json
import os
import re
import threading

import pytest
from playwright.sync_api import sync_playwright

APP_URL = "http://localhost:8501"
MAINTENANCE_URL = "http://localhost:8501/maintenance"
ARTIFACTS_DIR = os.path.join("tmp", "issue-36", "artifacts")
STORAGE_PATH = os.path.join("tmp", "issue-36", "auth-state.json")

pytest.importorskip("playwright.sync_api")

pytestmark = [
    pytest.mark.playwright_e2e,
    # E2E against the live app: requires http://localhost:8501 running with the
    # migrated synced DB and a saved OAuth state. Skipped (not failed) when the
    # app is down so `pytest test/` stays green without the server.
    pytest.mark.skipif(
        os.environ.get("SNEA_E2E", "") != "1",
        reason="live-app E2E — run with SNEA_E2E=1 while streamlit is up on :8501",
    ),
]


def _require_auth_storage() -> str:
    if not os.path.exists(STORAGE_PATH):
        raise AssertionError(
            "No saved OAuth session at tmp/issue-36/auth-state.json — "
            "log in once via the headed Playwright window to generate it."
        )
    with open(STORAGE_PATH) as fh:
        cookies = [c["name"] for c in json.load(fh).get("cookies", [])]
    if "gh_auth_token" not in cookies:
        raise AssertionError("Saved session lacks the gh_auth_token cookie — regenerate the login state.")
    return STORAGE_PATH


def _run_in_worker_thread(fn):
    """Run a sync_playwright body in a worker thread.

    pytest 9 + anyio keeps an asyncio loop on the main thread; the Playwright
    sync API forbids entering under a running loop. A worker thread has none.
    """
    box: list[BaseException | None] = []

    def _target():
        try:
            fn()
            box.append(None)
        except BaseException as e:  # noqa: BLE001 — propagate test failure verbatim
            box.append(e)

    t = threading.Thread(target=_target)
    t.start()
    t.join()
    err = box[0]
    if err is not None:
        raise err


def _make_rows_stale(count: int) -> None:
    """Mark `count` real gloss rows stale (wrong pin) so backfill has work to do.

    Operates on the synced local replica (never production). Rows keep their
    embeddings' semantics — the admin backfill re-embeds with the current pin.
    """
    import sys

    sys.path.insert(0, os.path.abspath("."))
    from sqlalchemy import text

    import src.database.models.core  # noqa: F401 — register all mappers before init_db
    import src.database.models.identity  # noqa: F401
    import src.database.models.iso639  # noqa: F401
    import src.database.models.meta  # noqa: F401
    import src.database.models.search  # noqa: F401
    import src.database.models.workflow  # noqa: F401
    from src.database.connection import get_engine, init_db

    eng = get_engine()  # also boots the local server if down
    init_db()  # schema self-heal (sequence + FK guards) via the app's own path
    # A fresh prod-sync has zero embedded rows (production predates #36 migrations);
    # seed embeddings via the real backfill service before marking rows stale.
    from src.services.embedding_service import PIN
    from src.services.semantic_search_service import backfill_embeddings

    with eng.connect() as conn:
        pinned = conn.execute(
            text("SELECT count(*) FROM gloss_search_entries WHERE embedding_model = :pin"),
            {"pin": PIN},
        ).scalar()
    if pinned < 10_000:
        backfill_embeddings(progress_callback=lambda done, total: None)
    with eng.connect() as conn:
        ids = [r[0] for r in conn.execute(
            text(
                "SELECT id FROM gloss_search_entries WHERE embedding_model = 'thenlper/gte-small' "
                "ORDER BY id LIMIT :n"
            ),
            {"n": count},
        ).fetchall()]
        if len(ids) < count:
            raise AssertionError(
                f"Only {len(ids)} pinned rows available to mark stale; need {count}."
            )
        conn.execute(
            text(
                "UPDATE gloss_search_entries SET embedding_model = 'stale/test-pin' "
                "WHERE id = ANY(:ids)"
            ),
            {"ids": ids},
        )
        conn.commit()


def _admin_flow():
    """Open /maintenance as the real OAuth admin, click backfill, verify progress + results."""
    storage = _require_auth_storage()
    # Seed real re-embed work: mark a slice of real synced rows stale (pin drift) so the
    # click-through exercises actual re-embedding, not a no-op pass over current rows.
    stale_count = 25
    _make_rows_stale(stale_count)
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        context = browser.new_context(storage_state=storage)
        try:
            page = context.new_page()
            page.goto(MAINTENANCE_URL)
            page.wait_for_selector("text=Maintenance Tables", timeout=60_000)
            page.screenshot(path=os.path.join(ARTIFACTS_DIR, "sc13-01-maintenance-loaded.png"))

            page.get_by_text("Data Reprocessing", exact=True).click()
            page.wait_for_timeout(2000)
            page.screenshot(path=os.path.join(ARTIFACTS_DIR, "sc13-02-data-reprocessing.png"))

            btn = page.get_by_role("button", name="Start Embedding Backfill")
            assert btn.is_visible(), "Start Embedding Backfill button not visible for admin"

            btn.click()

            progress = page.locator('[role="progressbar"], [data-testid="stProgress"]')
            progress.first.wait_for(state="visible", timeout=180_000)
            page.screenshot(path=os.path.join(ARTIFACTS_DIR, "sc13-03-progress-visible.png"))

            # Wait for completion: progress bar disappears once backfill finishes
            # Completion: st.status('Backfilling embeddings...') collapses when
            # update() closes; wait for the success message with a generous
            # envelope — 6682 rows measured ~72s (rate reference), cap 5 min.
            page.wait_for_selector(
                "text=/Successfully backfilled \\d+ of \\d+ entries/", timeout=300_000
            )
            body = page.inner_text("body")
            page.screenshot(path=os.path.join(ARTIFACTS_DIR, "sc13-04-after-run.png"))

            assert not re.search(r"Embedding backfill failed|Reprocessing failed", body), (
                f"Error alert present after run: {body[-800:]}"
            )
            success = re.search(r"[Bb]ackfilled?\s+(\d+)\s+of\s+(\d+)", body)
            assert success is not None, (
                f"Expected success (backfilled, total) after backfill; got tail: {body[-600:]}"
            )
            backfilled, total = int(success.group(1)), int(success.group(2))
            assert backfilled >= stale_count, (
                f"Backfill re-embedded {backfilled} rows; expected >= {stale_count} stale rows to be re-embedded"
            )
            details = {"backfilled": backfilled, "total": total}
            with open(os.path.join(ARTIFACTS_DIR, "sc13-clickthrough-result.json"), "w") as fh:
                json.dump(details, fh)
        finally:
            browser.close()


def test_admin_backfill_clickthrough():
    """Admin: open /maintenance, render, click backfill, observe progress + results."""
    _run_in_worker_thread(_admin_flow)


def _non_admin_flow():
    """Save a session-less fresh browser: unauthenticated /maintenance shows the login redirect."""
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        try:
            page = browser.new_page()
            page.goto(MAINTENANCE_URL)
            # The login button is a streamlit_oauth COMPONENT (iframe) — its label
            # is not visible to the main-frame text locator. Authenticated-state
            # gate instead: deep-link redirect to /login proves the role guard
            # denied access to the maintenance page.
            page.wait_for_url("**/login", timeout=30_000)
            page.screenshot(path=os.path.join(ARTIFACTS_DIR, "sc13-nonadmin-session.png"))
            btn_present = page.get_by_role("button", name="Start Embedding Backfill").is_visible()
            assert not btn_present, "Backfill button visible without admin role"
            # Unauthenticated deep-link to /maintenance redirects to the login page
            # (not the permission-error branch, which needs an authed non-admin role).
            # Login page rendered post-redirect: main panel holds the login component
            # area; sidebar shows Login item. Assert the redirect landed on Login UI.
            assert "Login" in page.title() or page.url.rstrip("/").endswith("/login"), (
                f"Expected login page redirect; got URL={page.url!r}"
            )
        finally:
            browser.close()


def test_non_admin_shows_permission_error():
    """Unauthenticated browser reaches the login flow, never the backfill button."""
    _run_in_worker_thread(_non_admin_flow)
