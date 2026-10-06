"""SC-7/SC-8/SC-9/SC-11: Playwright real-browser verification of the MDF
Reference page (.issues/1379 Phase 5).

Auth model: with SNEA_E2E=1 the app-side TEST-ONLY auth bypass hook
(src/services/security_manager.py) authenticates a FRESH browser context —
no saved storage state, no headed login (Issue #1400 SC-11 convention).
Harness conventions follow test_playwright_backfill_clickthrough.py:
sync_playwright bodies run in a worker thread; artifacts go to
tmp/issue-1379/artifacts/. Role-variant sessions (SC-10) live in
test_mdf_reference_roles_e2e.py.

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

import json
import os
import threading
import urllib.request

import pytest
from playwright.sync_api import sync_playwright

APP_URL = "http://localhost:8501"
MDF_URL = f"{APP_URL}/mdf-reference"
ARTIFACTS_DIR = os.path.join("tmp", "issue-1379", "artifacts")
MASTER_PATH = os.path.join("docs", "mdf", "build", "master.json")
PDF_PATH = os.path.join("docs", "mdf", "build", "mdf-lexical-fields-1.9a.pdf")

pytest.importorskip("playwright.sync_api")

pytestmark = [
    pytest.mark.playwright_e2e,
    # E2E against the live app: requires SNEA_E2E=1 and streamlit on :8501.
    # Skipped (not failed) without them so `pytest test/` stays green.
    pytest.mark.skipif(
        os.environ.get("SNEA_E2E", "") != "1",
        reason="live-app E2E — run with SNEA_E2E=1 while streamlit is up on :8501",
    ),
]


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


def _master_topics():
    with open(MASTER_PATH, encoding="utf-8") as fh:
        master = json.load(fh)
    return master


def _open_mdf_page():
    """Fresh browser context (SNEA_E2E bypass authenticates it) on the MDF
    Reference page; yields (pw, browser, page) — caller closes the browser.

    The wait targets page BODY content, not the sidebar nav label: the nav
    item renders before the page does, so matching "MDF Reference" alone
    races the cold-start compile.
    """
    pw = sync_playwright().start()
    browser = pw.chromium.launch()
    context = browser.new_context(storage_state=None)
    page = context.new_page()
    page.goto(MDF_URL)
    page.wait_for_selector("text=Helps Database for MDF Marker Set", timeout=60_000)
    return pw, browser, page


def test_sc7_renders_108_topics_17_chapters_lands_on_aa():
    """SC-7: all 108 keyed topics rendered, the 17 chapter groups present,
    and the landing entry is the source's home/TOC entry (aa)."""

    def flow():
        master = _master_topics()
        keys = [t["key"] for t in master["topics"]]
        chapter_keys = master["chapter_keys"]
        home_heading = next(
            t["heading"] or t["key"] for t in master["topics"] if t["key"] == master["home_key"]
        )
        pw, browser, page = _open_mdf_page()
        try:
            page.screenshot(path=os.path.join(ARTIFACTS_DIR, "sc7-01-landing.png"))

            # 17 chapter groups render as group headers
            h3_texts = page.eval_on_selector_all("h3", "els => els.map(e => e.innerText.trim())")
            assert len(h3_texts) == len(chapter_keys), (
                f"expected {len(chapter_keys)} chapter group headers, got {len(h3_texts)}: {h3_texts}"
            )

            # All 108 topic browser nodes present (button labels carry the keys)
            labels = page.eval_on_selector_all(
                "button", "els => els.map(e => e.innerText.trim())"
            )
            missing = [k for k in keys if k not in labels]
            assert not missing, f"{len(missing)} topic browser nodes missing: {missing[:10]}"

            # Landing entry is the home/TOC topic (aa)
            header = page.eval_on_selector_all("h2", "els => els.map(e => e.innerText.trim())")
            assert any(home_heading in h for h in header), (
                f"landing detail should show home entry heading {home_heading!r}; headers: {header}"
            )
            body = page.inner_text("body")
            assert "key aa" in body, f"detail pane should identify key aa; body tail: {body[-400:]}"

            with open(os.path.join(ARTIFACTS_DIR, "sc7-result.json"), "w") as fh:
                json.dump(
                    {
                        "topics": len(keys),
                        "chapter_groups": len(h3_texts),
                        "landing": home_heading,
                    },
                    fh,
                )
        finally:
            browser.close()
            pw.stop()

    _run_in_worker_thread(flow)


def test_sc7_unknown_deep_link_falls_back_to_home_with_notice():
    """Edge case: ?marker=zz falls back to the home entry with a visible
    notice — never an error or a blank pane."""

    def flow():
        master = _master_topics()
        home_heading = next(
            t["heading"] or t["key"] for t in master["topics"] if t["key"] == master["home_key"]
        )
        pw = sync_playwright().start()
        browser = pw.chromium.launch()
        try:
            page = browser.new_context(storage_state=None).new_page()
            page.goto(f"{MDF_URL}?marker=zz")
            page.wait_for_selector("text=No reference topic 'zz'", timeout=60_000)
            header = page.eval_on_selector_all("h2", "els => els.map(e => e.innerText.trim())")
            assert any(home_heading in h for h in header), (
                f"unknown deep link must land on home entry; headers: {header}"
            )
            page.screenshot(path=os.path.join(ARTIFACTS_DIR, "sc7-02-unknown-deeplink.png"))
        finally:
            browser.close()
            pw.stop()

    _run_in_worker_thread(flow)