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
    """Run a sync_playwright body in a worker thread and return its value.

    pytest 9 + anyio keeps an asyncio loop on the main thread; the Playwright
    sync API forbids entering under a running loop. A worker thread has none.
    """
    box: list[BaseException | None] = []
    result: list = []

    def _target():
        try:
            result.append(fn())
            box.append(None)
        except BaseException as e:  # noqa: BLE001 — propagate test failure verbatim
            box.append(e)

    t = threading.Thread(target=_target)
    t.start()
    t.join()
    err = box[0]
    if err is not None:
        raise err
    return result[0] if result else None


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


def test_sc8_cf_target_button_navigates_from_aa_toc():
    """SC-8 spot-check: a \\cf target rendered in the home entry's TOC block
    navigates in-app to its topic and the deep-link URL updates."""

    def flow():
        pw, browser, page = _open_mdf_page()
        try:
            # cf target buttons live in the detail column (right); the browser
            # column (left) has same-labeled topic nodes, so scope to it. The
            # home TOC names Introduction in several cf rows — any of its
            # target buttons navigates there.
            main_col = page.locator('[data-testid="stColumn"]').nth(1)
            main_col.get_by_role("button", name="Introduction", exact=True).first.click()
            # Scope to the detail-pane h2: the same text also appears as the
            # Introduction chapter's left-column group header (h3), which is
            # present before navigation and would satisfy a plain text wait.
            page.wait_for_selector(
                'h2:has-text("Standard Lexical Database Field Markers")', timeout=30_000
            )
            # The query param is pushed to the URL asynchronously after the
            # rerun renders — wait for it rather than reading immediately.
            page.wait_for_url("**marker=Introduction*", timeout=15_000)
            assert "marker=Introduction" in page.url, f"deep-link URL not updated: {page.url}"
            page.screenshot(path=os.path.join(ARTIFACTS_DIR, "sc8-01-toc-navigation.png"))
        finally:
            browser.close()
            pw.stop()

    _run_in_worker_thread(flow)


def test_sc8_cf_target_button_navigates_from_marker_entry():
    """SC-8 spot-check: the lx entry's \\cf to lc navigates to the lc topic."""

    def flow():
        pw = sync_playwright().start()
        browser = pw.chromium.launch()
        try:
            page = browser.new_context(storage_state=None).new_page()
            page.goto(f"{MDF_URL}?marker=lx")
            page.wait_for_selector("text=lexeme or headword", timeout=60_000)
            main_col = page.locator('[data-testid="stColumn"]').nth(1)
            main_col.get_by_role("button", name="lc", exact=True).first.click()
            # lx's own body text mentions "lexical citation", so a plain text
            # wait would pass before navigation — scope to the detail h2.
            page.wait_for_selector('h2:has-text("lexical citation")', timeout=30_000)
            page.wait_for_url("**marker=lc*", timeout=15_000)
            header = page.eval_on_selector_all("h2", "els => els.map(e => e.innerText.trim())")
            assert any("lc" in h for h in header), f"expected lc detail; headers: {header}"
            page.screenshot(path=os.path.join(ARTIFACTS_DIR, "sc8-02-cf-navigation.png"))
        finally:
            browser.close()
            pw.stop()

    _run_in_worker_thread(flow)


def _filter_flow(query: str, screenshot_name: str):
    """Type a filter query into the MDF Reference browser and return the
    left-column state (button labels, h3 count, body text) for assertions."""

    def flow():
        pw, browser, page = _open_mdf_page()
        try:
            left_col = page.locator('[data-testid="stColumn"]').nth(0)
            flt = page.get_by_label("Filter topics")
            flt.wait_for(state="visible", timeout=30_000)
            flt.fill(query)
            flt.press("Enter")
            page.wait_for_timeout(2500)
            labels = [t.strip() for t in left_col.locator("button").all_inner_texts()]
            h3_count = len(page.query_selector_all("h3"))
            body = page.inner_text("body")
            page.screenshot(path=os.path.join(ARTIFACTS_DIR, screenshot_name))
            return {"labels": labels, "h3_count": h3_count, "body": body}
        finally:
            browser.close()
            pw.stop()

    return flow()


def test_sc9_filter_matches_accented_definition_text():
    """SC-9: the accented source term 'léwat' matches exactly the lc topic —
    the diacritic survives the filter losslessly."""
    state = _run_in_worker_thread(lambda: _filter_flow("léwat", "sc9-01-accented-lewat.png"))
    # The left browser column also carries the R-13 PDF download control —
    # assert on the topic-match buttons only.
    topic_labels = [lbl for lbl in state["labels"] if lbl != "Download the MDF reference (PDF)"]
    assert topic_labels == ["lc"], f"expected only lc for 'léwat'; got {topic_labels}"
    assert state["h3_count"] == 0, "filter mode must replace the chapter tree (no h3 headers)"


def test_sc9_filter_case_insensitive_accented_query():
    """SC-9: an uppercase accented query ('ADÁ') matches the lowercase source
    content in the Alternate_Hierarchy chapter topic."""
    state = _run_in_worker_thread(lambda: _filter_flow("ADÁ", "sc9-02-accented-ADÁ.png"))
    assert "Alternate_Hierarchy" in state["labels"], (
        f"uppercase accented query must match; got {state['labels']}"
    )


def test_sc9_filter_no_matches_shows_info_banner():
    """Edge case: an empty filter result renders the standard empty-state
    info banner, not a blank column."""
    state = _run_in_worker_thread(lambda: _filter_flow("zzzznope", "sc9-03-empty-state.png"))
    assert "No topics match your filter." in state["body"], (
        f"empty-state banner missing; body tail: {state['body'][-400:]}"
    )


def test_sc11_pdf_download_serves_committed_bytes():
    """SC-11: the download control serves a file named
    mdf-lexical-fields-1.9a.pdf whose bytes are identical to the committed
    deliverable (checksum-compared)."""

    def flow():
        import hashlib

        pw, browser, page = _open_mdf_page()
        try:
            with page.expect_download(timeout=30_000) as download_info:
                page.get_by_role("button", name="Download the MDF reference (PDF)").click()
            download = download_info.value
            assert download.suggested_filename == "mdf-lexical-fields-1.9a.pdf", (
                f"served filename {download.suggested_filename!r} violates R-14"
            )
            target = os.path.join(ARTIFACTS_DIR, "sc11-downloaded.pdf")
            download.save_as(target)
            served_sha = hashlib.sha256(open(target, "rb").read()).hexdigest()
            with open(PDF_PATH, "rb") as fh:
                committed_sha = hashlib.sha256(fh.read()).hexdigest()
            assert served_sha == committed_sha, (
                f"served PDF bytes differ from the committed file "
                f"(served {served_sha[:16]}…, committed {committed_sha[:16]}…)"
            )
            with open(os.path.join(ARTIFACTS_DIR, "sc11-result.json"), "w") as fh:
                json.dump({"filename": download.suggested_filename, "sha256": served_sha}, fh)
        finally:
            browser.close()
            pw.stop()

    _run_in_worker_thread(flow)
