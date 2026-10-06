"""SC-12: Playwright real-browser verification of the in-context MDF
reference hooks on the three MDF-touching surfaces (.issues/1379 Phase 6,
R-11): Direct Entry per-field marker links, Records marker tooltips + per-
record marker help, and Upload MDF review warning links.

Auth model: with SNEA_E2E=1 the app-side TEST-ONLY auth bypass hook
(src/services/security_manager.py) authenticates a FRESH browser context —
no saved storage state, no headed login (Issue #1400 SC-11 convention).
Harness conventions follow test_mdf_reference_e2e.py: sync_playwright bodies
run in a worker thread; artifacts go to tmp/issue-1379/artifacts/.

The deep-link under test: st.page_link(..., query_params={"marker": <key>})
navigates in-session to /mdf-reference?marker=<key>, which the MDF Reference
page resolves via st.query_params.

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

import json
import os
import threading

import pytest
from playwright.sync_api import sync_playwright

APP_URL = "http://localhost:8501"
ARTIFACTS_DIR = os.path.join("tmp", "issue-1379", "artifacts")
MASTER_PATH = os.path.join("docs", "mdf", "build", "master.json")

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


def _marker_definition(key: str) -> str:
    """The expected one-line definition of a marker from the committed
    master.json (the same source the hooks read)."""
    with open(MASTER_PATH, encoding="utf-8") as fh:
        master = json.load(fh)
    topic = next(t for t in master["topics"] if t["key"] == key)
    heading = topic["heading"]
    # \marker + one separator whitespace; the remainder is the definition.
    token, _, rest = heading.partition(" ")
    assert token == f"\\{key}"
    return rest.strip()


def _fresh_page():
    """Fresh browser context (SNEA_E2E bypass authenticates it); yields
    (pw, browser, page) — caller closes the browser."""
    pw = sync_playwright().start()
    browser = pw.chromium.launch()
    context = browser.new_context(storage_state=None)
    page = context.new_page()
    return pw, browser, page


def _assert_deep_link_navigates_to_entry(page, key: str, heading_snippet: str):
    """Click the page_link for a marker and assert it lands on that marker's
    MDF Reference entry (correct link target, not just a correct href)."""
    page.locator(f"a[data-testid='stPageLink-NavLink'][href*='marker={key}']").first.click()
    page.wait_for_url(f"**marker={key}*", timeout=30_000)
    page.wait_for_selector(f"text={heading_snippet}", timeout=60_000)


# ── (a) Direct Entry ───────────────────────────────────────────────────


def test_sc12_direct_entry_per_field_hooks_link_to_reference():
    """R-11a: each field carries a reference expander; after a submission the
    markers typed into that field render as links targeting their own
    reference entries; the static home link is present too."""

    def flow():
        pw, browser, page = _fresh_page()
        try:
            page.goto(f"{APP_URL}/direct-entry")
            page.wait_for_selector("text=Direct Record Entry", timeout=60_000)

            # The per-field reference expander is present (collapsed) even
            # before anything is submitted.
            expander = page.locator("details summary:has-text('Marker reference — Record(s) 1')")
            expander.wait_for(state="visible", timeout=30_000)

            # The static reference hook targets the reference home entry.
            home_link = page.locator("a[data-testid='stPageLink-NavLink'][href*='marker=aa']").first
            assert "mdf-reference?marker=aa" in (home_link.get_attribute("href") or "")

            # Type a record that is rejected on submit (the \\lemma guard) so
            # the user stays on this page with the typed text preserved —
            # exactly the situation where in-context help matters.
            field = page.get_by_label("Record(s) 1", exact=True)
            field.fill("\\lx zzprobe\n\\lemma zz probe")
            page.get_by_role("button", name="Submit Records").click()
            page.wait_for_selector("text=Submission aborted", timeout=30_000)

            # The expander now lists the markers typed into field 1, each as
            # a link to its own reference entry.
            expander.click()
            lx_href = page.locator(
                "details:has(summary:has-text('Marker reference — Record(s) 1')) "
                "a[data-testid='stPageLink-NavLink'][href*='marker=lx']"
            ).first.get_attribute("href")
            lemma_href = page.locator(
                "details:has(summary:has-text('Marker reference — Record(s) 1')) "
                "a[data-testid='stPageLink-NavLink'][href*='marker=lemma']"
            ).first.get_attribute("href")
            assert lx_href and lx_href.endswith("mdf-reference?marker=lx"), lx_href
            assert lemma_href and lemma_href.endswith("mdf-reference?marker=lemma"), lemma_href
            page.screenshot(path=os.path.join(ARTIFACTS_DIR, "sc12-01-direct-entry-hooks.png"))

            # The \\lx link lands on the \\lx reference entry.
            _assert_deep_link_navigates_to_entry(page, "lx", "lexeme or headword")
            page.screenshot(path=os.path.join(ARTIFACTS_DIR, "sc12-02-direct-entry-lx-target.png"))
        finally:
            browser.close()
            pw.stop()

    _run_in_worker_thread(flow)


# ── (b) Records ────────────────────────────────────────────────────────


def _find_mdf_block_span(page):
    """Return the first .mdf-marker span inside a rendered MDF block.

    st.html renders inside an iframe, so every same-origin iframe document is
    scanned (the pattern established by test_mdf_block_search_mark_dom_sc10).
    """
    return page.evaluate(
        """() => {
        const docs = [document];
        for (const frame of document.querySelectorAll('iframe')) {
            try {
                if (frame.contentDocument) docs.push(frame.contentDocument);
            } catch (e) {}
        }
        for (const doc of docs) {
            const span = doc.querySelector('.mdf-wrap-block .mdf-marker');
            if (span) return {title: span.getAttribute('title'), text: span.textContent};
        }
        return null;
    }"""
    )


def test_sc12_records_marker_tooltip_and_help_expander():
    """R-11b: a marker token in a rendered MDF block exposes that marker's
    definition on interaction (title tooltip), and the per-record marker-help
    expander lists the record's markers with deep links to their entries."""

    def flow():
        pw, browser, page = _fresh_page()
        try:
            page.goto(f"{APP_URL}/records")
            page.wait_for_selector("text=Record #", timeout=60_000)

            # Tooltip: the first line of a record is \lx; its token span must
            # carry the lx definition from the committed reference data.
            expected = _marker_definition("lx")
            span = None
            for _ in range(20):
                span = _find_mdf_block_span(page)
                if span:
                    break
                page.wait_for_timeout(500)
            assert span is not None, "no marker tooltip span found in any rendered MDF block"
            assert span["title"] == expected, (
                f"marker tooltip must carry the lx definition {expected!r}; got {span['title']!r}"
            )
            assert span["text"] == "\\lx", span["text"]
            page.screenshot(path=os.path.join(ARTIFACTS_DIR, "sc12-03-records-tooltip.png"))

            # Per-record marker help: expand the first record's expander and
            # follow its \\lx deep link to the correct reference entry.
            expander = page.locator("details summary:has-text('Marker help')").first
            expander.wait_for(state="visible", timeout=30_000)
            expander.click()
            _assert_deep_link_navigates_to_entry(page, "lx", "lexeme or headword")
            page.screenshot(path=os.path.join(ARTIFACTS_DIR, "sc12-04-records-lx-target.png"))
        finally:
            browser.close()
            pw.stop()

    _run_in_worker_thread(flow)


# ── (c) Upload MDF review ──────────────────────────────────────────────


def test_sc12_upload_review_flagged_marker_links_to_reference():
    """R-11c: a staged entry carrying a legacy marker (\\na) renders a
    warning whose link opens that marker's own reference entry. Staging goes
    through the app's normal Direct Entry flow (its valid-submit path stages
    and switches to the Upload review view)."""

    def flow():
        pw, browser, page = _fresh_page()
        try:
            page.goto(f"{APP_URL}/direct-entry")
            page.wait_for_selector("text=Direct Record Entry", timeout=60_000)

            # Test scaffolding: plainly synthetic tokens with standard MDF
            # markers plus the legacy \na tag (1 invalid of 7 tags — below
            # the parser's 20% unrecognized-tag watermark, so it stages).
            field = page.get_by_label("Record(s) 1", exact=True)
            field.fill(
                "\\lx zztestlexeme\n\\ps noun\n\\ge zz test gloss\n"
                "\\nt zz entry note\n\\so zz test source\n\\dt 2026-10-06\n"
                "\\na zz ethnographic note"
            )
            page.get_by_role("button", name="Submit Records").click()

            # Valid submission stages the batch and switches to the review
            # view, where the flagged marker must surface a warning with a
            # link to that marker's reference entry.
            page.wait_for_selector("text=zztestlexeme", timeout=90_000)
            warning = page.locator("div[data-testid='stAlert']:has-text('Marker check')").first
            warning.wait_for(state="visible", timeout=30_000)
            na_link = page.locator("a[data-testid='stPageLink-NavLink'][href*='marker=na']").first
            href = na_link.get_attribute("href")
            assert href and href.endswith("mdf-reference?marker=na"), href
            page.screenshot(path=os.path.join(ARTIFACTS_DIR, "sc12-05-upload-review-warning.png"))

            _assert_deep_link_navigates_to_entry(page, "na", "notes on anthropology")
            page.screenshot(path=os.path.join(ARTIFACTS_DIR, "sc12-06-upload-review-na-target.png"))
        finally:
            browser.close()
            pw.stop()

    _run_in_worker_thread(flow)
