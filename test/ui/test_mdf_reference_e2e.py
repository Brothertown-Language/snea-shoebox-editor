"""SC-7/SC-8/SC-9/SC-11: Playwright real-browser verification of the MDF
Reference page (issue #1379 Phase 5).

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
import time

import pytest
from playwright.sync_api import sync_playwright

# App port parameterized (SNEA_E2E_PORT) so the harness can run against a
# dedicated app instance without touching a developer-owned app on :8501.
E2E_PORT = os.environ.get("SNEA_E2E_PORT", "8501")
APP_URL = f"http://localhost:{E2E_PORT}"
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
    """SC-7: all 108 keyed topics rendered, the 17 chapter groups plus the
    terminal Field Marker Reference section present as group headers, and the
    landing entry is the source's home/TOC entry (aa)."""

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

            # 17 chapter groups + the terminal reference section render as
            # group headers (semantic regrouping, holistic with PDF/HTML).
            h3_texts = page.eval_on_selector_all("h3", "els => els.map(e => e.innerText.trim())")
            assert len(h3_texts) == len(chapter_keys) + 1, (
                f"expected {len(chapter_keys) + 1} group headers "
                f"(chapters + Field Marker Reference), got {len(h3_texts)}: {h3_texts}"
            )
            assert "Field Marker Reference" in h3_texts, (
                f"terminal reference section header missing: {h3_texts}"
            )

            # All 108 topic browser nodes present: topic keys render as bare
            # button labels; the home/TOC entry is labeled plain "Home" for
            # users (2026-10-06 directive: no bare aa in any user-facing
            # label) and is asserted by its user label.
            home_key = master["home_key"]
            labels = page.eval_on_selector_all(
                "button", "els => els.map(e => e.innerText.trim())"
            )
            missing = [k for k in keys if k != home_key and k not in labels]
            assert not missing, f"{len(missing)} topic browser nodes missing: {missing[:10]}"
            assert "Home" in labels, (
                f"the home/TOC entry button must read plain Home; labels head: {labels[:10]}"
            )
            assert f"Home ({home_key})" not in labels, (
                "the parenthesized bare key must not render in the home button label"
            )

            # Single left rail (vision-review remediation): the global sidebar
            # nav stays hidden and the standard back-to-main affordance rides
            # the MDF browser column.
            nav = page.locator('[data-testid="stSidebarNav"]')
            assert nav.count() == 0 or not nav.first.is_visible(), (
                "the global sidebar nav must stay hidden on the MDF Reference page"
            )
            assert page.get_by_role("button", name="Back to Main Menu").count() >= 1, (
                "the back-to-main affordance must ride the MDF browser rail"
            )

            # Landing entry is the home/TOC topic (aa)
            header = page.eval_on_selector_all("h2", "els => els.map(e => e.innerText.trim())")
            assert any(home_heading in h for h in header), (
                f"landing detail should show home entry heading {home_heading!r}; headers: {header}"
            )
            body = page.inner_text("body")
            # 2026-10-06 directive: the "key aa · source line N" caption is
            # gone — the heading and structure carry the topic's identity.
            assert "key aa" not in body, "the key caption must no longer render in the detail pane"
            assert home_heading in body, (
                f"detail pane should show the home entry heading {home_heading!r}; body tail: {body[-400:]}"
            )

            with open(os.path.join(ARTIFACTS_DIR, "sc7-result.json"), "w") as fh:
                json.dump(
                    {
                        "topics": len(keys),
                        "chapter_groups": len(chapter_keys),
                        "group_headers": len(h3_texts),
                        "landing": home_heading,
                    },
                    fh,
                )
        finally:
            browser.close()
            pw.stop()

    _run_in_worker_thread(flow)


def test_sc7_reference_section_structure_and_chapter_members():
    """Semantic regrouping: the terminal Field Marker Reference section renders
    its five groups (Record Marker → Basic Fields → Reserved Fields → Optional
    Fields → Discontinued) with lx under Record Marker, hm/lc/se/sn under
    Reserved, xg under Discontinued, the Basic entries alphabetical, and the
    multi-key verb-paradigm stub still under Old_and_Changed_Markers."""

    def flow():
        pw, browser, page = _open_mdf_page()
        try:
            page.screenshot(path=os.path.join(ARTIFACTS_DIR, "sc7-03-reference-section.png"))
            left_col = page.locator('[data-testid="stColumn"]').nth(0)
            scan = left_col.locator("h3, h4, button").evaluate_all(
                "els => els.map(e => [e.tagName, e.innerText.trim()])"
            )

            def group_slice(start_text, start_tag, stop_tags):
                """Button labels strictly between the named header and the next
                header of any stop tag, in DOM order."""
                at_start = False
                labels = []
                for tag, text in scan:
                    if not at_start:
                        if tag == start_tag and text == start_text:
                            at_start = True
                        continue
                    if tag in stop_tags:
                        break
                    if tag == "BUTTON":
                        labels.append(text)
                assert at_start, f"header {start_text!r} not found in browser column"
                return labels

            headers_h3 = [text for tag, text in scan if tag == "H3"]
            headers_h4 = [text for tag, text in scan if tag == "H4"]
            assert headers_h4 == [
                "Record Marker",
                "Basic Fields",
                "Reserved Fields",
                "Optional Fields",
                "Discontinued",
            ], f"reference group headers wrong: {headers_h4}"
            assert headers_h3[-1] == "Field Marker Reference", (
                f"reference section must be the terminal group; h3 tail: {headers_h3[-3:]}"
            )

            assert group_slice("Record Marker", "H4", {"H3", "H4"}) == ["lx"]
            basic = group_slice("Basic Fields", "H4", {"H3", "H4"})
            assert len(basic) == 17 and basic == sorted(basic) and "lx" not in basic, (
                f"Basic Fields must hold its 17 entries alphabetical: {basic}"
            )
            assert group_slice("Reserved Fields", "H4", {"H3", "H4"}) == ["hm", "lc", "se", "sn"]
            optional = group_slice("Optional Fields", "H4", {"H3", "H4"})
            assert len(optional) == 66 and optional == sorted(optional), (
                f"Optional Fields must hold 66 entries alphabetical: {optional[:5]}…"
            )
            assert group_slice("Discontinued", "H4", {"H3", "H4"}) == ["xg"]

            # The multi-key verb-paradigm stub stays inside its chapter group
            # (source-directed via its own \\cf), and no marker-definition
            # topic renders inside any chapter group anymore.
            stub_key = "1s 1p 1e 1i 1d 2s 2p 2d 3s 3p 3d 4s 4p 4d"
            reference_keys = {"lx", "hm", "lc", "se", "sn", "xg"} | set(basic) | set(optional)
            chapter_slices = []
            current_header, current_labels = None, []
            for tag, text in scan:
                if tag == "H3":
                    if current_header is not None:
                        chapter_slices.append((current_header, current_labels))
                    current_header, current_labels = text, []
                elif tag == "H4":
                    break  # reached the reference section — chapters are done
                elif tag == "BUTTON" and current_header is not None:
                    current_labels.append(text)
            chapter_slices.append((current_header, current_labels))
            by_chapter = dict(chapter_slices)
            assert stub_key in by_chapter.get("Old and Changed Markers", []), (
                f"numeric stub must render under Old and Changed Markers; "
                f"that chapter's buttons: {by_chapter.get('Old and Changed Markers')}"
            )
            for header, labels in chapter_slices:
                stray = [lbl for lbl in labels if lbl in reference_keys]
                assert not stray, f"marker-definition topics leaked into chapter {header!r}: {stray}"

            with open(os.path.join(ARTIFACTS_DIR, "sc7-structure-result.json"), "w") as fh:
                json.dump(
                    {
                        "reference_groups": headers_h4,
                        "basic_count": len(basic),
                        "optional_count": len(optional),
                        "stub_under": "Old and Changed Markers",
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


def test_cf_lookup_pairs_render_as_per_pair_rows():
    """2026-10-06 change control: the Introduction detail pane renders the shd4
    group "Information Relating Directly to the Headword" as a per-pair list —
    the marker as a deep-link button with its gloss beside it — not a single
    run-together line. 2026-10-06 paren-depth rule: the va row carries its
    full parenthetical gloss "variant form (also ve* comments)" (unsplit) and
    the in-gloss ve* mention is a live deep link to the ve topic."""

    def flow():
        pw, browser, page = _open_mdf_page()
        try:
            page.goto(f"{MDF_URL}?marker=Introduction")
            heading = page.locator('h6:has-text("Information Relating Directly to the Headword")')
            heading.wait_for(timeout=60_000)
            heading.scroll_into_view_if_needed()
            main_col = page.locator('[data-testid="stColumn"]').nth(1)

            def pair_row(marker_label: str) -> object:
                button = main_col.get_by_role("button", name=marker_label, exact=True).first
                return button.locator("xpath=ancestor::div[@data-testid='stHorizontalBlock'][1]")

            lx_row = pair_row("lx")
            assert "lexeme" in lx_row.inner_text(), (
                f"lx row must carry its gloss beside the marker: {lx_row.inner_text()!r}"
            )
            assert "homonym" not in lx_row.inner_text(), (
                f"lx row must not run together with hm: {lx_row.inner_text()!r}"
            )
            hm_row = pair_row("hm")
            assert "homonym number" in hm_row.inner_text(), f"hm row gloss missing: {hm_row.inner_text()!r}"
            sn_row = pair_row("sn")
            assert "sense number" in sn_row.inner_text(), f"sn row gloss missing: {sn_row.inner_text()!r}"

            body = page.inner_text("body")
            assert "→ lx lexeme" not in body, "run-together cf caption must be gone for the glossed group"

            # Paren-depth rule: the va gloss stays one unsplit string in its
            # own row, with the parenthetical cross-reference intact.
            va_row = pair_row("va")
            va_row.scroll_into_view_if_needed()
            va_text = va_row.inner_text()
            assert "variant form (also ve* comments)" in va_text, (
                f"va row must carry the unsplit parenthetical gloss: {va_text!r}"
            )
            assert "morphology" not in va_text, f"va row must not run together with mr: {va_text!r}"
            ve_link = va_row.get_by_role("link", name="ve*")
            assert ve_link.count() == 1, "the in-gloss ve* mention must render as a live link"
            assert "marker=ve" in ve_link.first.get_attribute("href"), (
                f"ve* link must deep-link via ?marker=ve: {ve_link.first.get_attribute('href')!r}"
            )
            pdl_row = pair_row("pdl")
            assert "paradigm label (also pdv* paradigm form & glosses)" in pdl_row.inner_text(), (
                f"pdl row must carry the unsplit parenthetical gloss: {pdl_row.inner_text()!r}"
            )
            assert pdl_row.get_by_role("link", name="pdv*").count() == 1, (
                "the in-gloss pdv* mention must render as a live link"
            )
            page.screenshot(path=os.path.join(ARTIFACTS_DIR, "cf-pairs-headword-rows.png"))
            va_row.screenshot(path=os.path.join(ARTIFACTS_DIR, "cf-pairs-va-row-unsplit.png"))

            # Click-through: the ve* mention deep-links to the ve topic.
            # Streamlit renders markdown links target="_blank" — the navigation
            # may land in a new context page; accept either surface.
            ve_link.first.click()
            deadline = time.monotonic() + 60
            target = None
            while time.monotonic() < deadline and target is None:
                for candidate in page.context.pages:
                    if "marker=ve" in candidate.url:
                        target = candidate
                        break
                if target is None:
                    page.wait_for_timeout(250)
            assert target is not None, "clicking the ve* mention must navigate to ?marker=ve"
            target.bring_to_front()
            target.wait_for_selector('h2:has-text("variant comment")', timeout=60_000)
            # 2026-10-06 directive: the "key ve · …" caption is gone — the
            # heading and structure carry the topic's identity.
            assert "key ve" not in target.inner_text("body"), (
                "the key caption must no longer render in the detail pane"
            )
            target.screenshot(path=os.path.join(ARTIFACTS_DIR, "cf-pairs-ve-mention-navigation.png"))
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
            # Session-start reruns can transiently mount the browser column
            # twice (two identically-labeled inputs; observed intermittently
            # and reproduced on the pre-change branch 2026-10-06). Interact
            # only once a single live input has settled — filling during the
            # transient window hits strict-mode ambiguity or the stale mount.
            deadline = time.monotonic() + 30
            while True:
                if flt.count() == 1:
                    page.wait_for_timeout(400)
                    if flt.count() == 1:
                        break
                if time.monotonic() > deadline:
                    pytest.fail(f"filter input did not settle to one element (count={flt.count()})")
                page.wait_for_timeout(200)
            flt.wait_for(state="visible", timeout=30_000)
            flt.fill(query)
            flt.press("Enter")
            page.wait_for_timeout(2500)
            labels = [
                t.strip()
                for t in left_col.locator("button:not(.mdf-split-toggle)").all_inner_texts()
            ]
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
    # The left browser column also carries the R-13 PDF download control, the
    # standard back-to-main affordance, and the split-pane « toggle (a
    # JS-injected control strip button, not a topic node) — assert on the
    # topic-match buttons only. (Button inner_text embeds the icon and
    # newlines, so the rail controls match by substring.)
    rail_controls = ("Download the MDF reference (PDF)", "Back to Main Menu")
    topic_labels = [
        lbl for lbl in state["labels"] if not any(control in lbl for control in rail_controls)
    ]
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


def test_filter_home_topic_chip_reads_home():
    """2026-10-06 directive: the filter-mode chip for the home topic reads
    plain "Home" — no bare aa in any user-facing label (all other matching
    chips stay as their bare marker keys). Deep-link navigation by the aa
    key itself is unaffected."""

    def flow():
        home_key = _master_topics()["home_key"]
        state = _filter_flow("Helps Database", os.path.join("vision3", "09-home-label-plain.png"))
        # The left browser column also carries the rail controls (download,
        # back-to-main) — assert on the topic-match chips only, as in SC-9.
        rail_controls = ("Download the MDF reference (PDF)", "Back to Main Menu")
        topic_labels = [
            lbl for lbl in state["labels"] if not any(control in lbl for control in rail_controls)
        ]
        assert topic_labels == ["Home"], (
            f"the home topic's filter chip must read plain Home; got {topic_labels}"
        )
        assert "aa" not in topic_labels, (
            f"the bare home key must not render as a filter chip label; got {topic_labels}"
        )
        # The chip still navigates by the aa key internally: clicking it
        # lands on the home entry (heading assertion unchanged).
        pw, browser, page = _open_mdf_page()
        try:
            left_col = page.locator('[data-testid="stColumn"]').nth(0)
            flt = page.get_by_label("Filter topics")
            flt.wait_for(state="visible", timeout=30_000)
            flt.fill("Helps Database")
            flt.press("Enter")
            page.wait_for_timeout(2500)
            left_col.get_by_role("button", name="Home", exact=True).first.click()
            page.wait_for_url(f"**marker={home_key}*", timeout=30_000)
            page.wait_for_timeout(1500)
            header = page.eval_on_selector_all("h2", "els => els.map(e => e.innerText.trim())")
            assert any("Helps Database for MDF Marker Set" in h for h in header), (
                f"the Home chip must land on the home entry; headers: {header}"
            )
            # The aa deep link still navigates to the home entry.
            page.goto(f"{MDF_URL}?marker={home_key}")
            page.wait_for_selector("text=Helps Database for MDF Marker Set", timeout=60_000)
            header = page.eval_on_selector_all("h2", "els => els.map(e => e.innerText.trim())")
            assert any("Helps Database for MDF Marker Set" in h for h in header), (
                f"?marker={home_key} deep link must land on the home entry; headers: {header}"
            )
        finally:
            browser.close()
            pw.stop()

    _run_in_worker_thread(flow)


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


# ── Split-pane layout (2026-10-06 developer layout directive) ──────────
#
# The MDF Reference page renders as a fixed-height split: the left browser
# rail scrolls independently of the detail pane, a drag handle between the
# panes resizes the rail (persisted), a «/» control hides/shows the rail
# (persisted), and any navigation (topic click, cf cross-reference,
# ?marker= deep link) lands the detail pane at ITS top while the rail keeps
# its own scroll position. Assertions target the page's contract, not the
# injection mechanism.


def _split_panes(page):
    """(rail, detail) — the two stColumns of the MDF split, in DOM order."""
    rail = page.locator('[data-testid="stColumn"]').nth(0)
    detail = page.locator('[data-testid="stColumn"]').nth(1)
    return rail, detail


def test_split_drag_resizes_rail_and_persists_across_rerun():
    """(a) dragging the handle widens the rail and the width survives a
    topic-click rerun."""

    def flow():
        pw, browser, page = _open_mdf_page()
        try:
            handle = page.locator(".mdf-split-handle")
            handle.wait_for(state="visible", timeout=30_000)
            rail, _detail = _split_panes(page)
            w0 = rail.bounding_box()["width"]
            box = handle.bounding_box()
            cx, cy = box["x"] + box["width"] / 2, box["y"] + 300
            page.mouse.move(cx, cy)
            page.mouse.down()
            page.mouse.move(cx + 150, cy, steps=10)
            page.mouse.up()
            page.wait_for_timeout(400)
            w1 = rail.bounding_box()["width"]
            assert w1 >= w0 + 140, f"dragging +150px must widen the rail: {w0:.0f} -> {w1:.0f}"
            page.screenshot(path=os.path.join(ARTIFACTS_DIR, "vision3", "split-a-dragged.png"))
            # Persistence: a topic click reruns the app; the width must hold.
            rail.get_by_role("button", name="ge", exact=True).first.click()
            page.wait_for_url("**marker=ge*", timeout=30_000)
            page.wait_for_timeout(800)
            w2 = rail.bounding_box()["width"]
            assert abs(w2 - w1) < 3, f"rail width must persist across a rerun: {w1:.0f} -> {w2:.0f}"
        finally:
            browser.close()
            pw.stop()

    _run_in_worker_thread(flow)


def test_split_independent_scrolling_on_navigation():
    """(b) with the rail scrolled deep down, navigating to a topic found
    there shows it in the detail pane AT ITS TOP while the rail keeps its
    own scroll position."""

    def flow():
        pw, browser, page = _open_mdf_page()
        try:
            rail, detail = _split_panes(page)
            rail.evaluate("el => { el.scrollTop = el.scrollHeight; }")
            page.wait_for_timeout(400)
            s0 = rail.evaluate("el => el.scrollTop")
            assert s0 > 400, f"the rail must be its own scroll container (scrolled to {s0})"
            # The terminal Discontinued topic (xg) sits at the rail's bottom.
            rail.get_by_role("button", name="xg", exact=True).first.click()
            page.wait_for_selector('h2:has-text("(discontinued field)")', timeout=30_000)
            page.wait_for_timeout(1500)  # let the scroll-to-top settle window elapse
            s1 = rail.evaluate("el => el.scrollTop")
            assert abs(s1 - s0) < 60, f"rail scroll must survive navigation: {s0:.0f} -> {s1:.0f}"
            dtop = detail.evaluate("el => el.scrollTop")
            assert dtop < 10, f"the detail pane must land at its own top: {dtop}"
            page.screenshot(path=os.path.join(ARTIFACTS_DIR, "vision3", "split-b-independent-scroll.png"))
        finally:
            browser.close()
            pw.stop()

    _run_in_worker_thread(flow)


def test_split_deeplink_lands_with_detail_at_top():
    """(c) a ?marker= deep link lands with the detail pane scrolled to its
    own top, showing the requested marker's content."""

    def flow():
        pw = sync_playwright().start()
        browser = pw.chromium.launch()
        try:
            page = browser.new_context(storage_state=None).new_page()
            page.goto(f"{MDF_URL}?marker=ge")
            page.wait_for_selector("text=gloss (English)", timeout=60_000)
            page.wait_for_timeout(1500)  # settle window
            _rail, detail = _split_panes(page)
            dtop = detail.evaluate("el => el.scrollTop")
            assert dtop < 10, f"deep link must land with the detail pane at its top: {dtop}"
            page.screenshot(path=os.path.join(ARTIFACTS_DIR, "vision3", "split-c-deeplink-top.png"))
        finally:
            browser.close()
            pw.stop()

    _run_in_worker_thread(flow)


def test_split_hide_show_rail_persists_state():
    """(d) the «/» control hides the rail and shows it again at the persisted
    width; the collapsed state survives a rerun."""

    def flow():
        pw, browser, page = _open_mdf_page()
        try:
            handle = page.locator(".mdf-split-handle")
            handle.wait_for(state="visible", timeout=30_000)
            rail, detail = _split_panes(page)
            w0 = rail.bounding_box()["width"]
            page.locator(".mdf-split-toggle").click()
            page.wait_for_timeout(400)
            assert rail.bounding_box() is None, "the rail must be hidden after the « toggle"
            page.screenshot(path=os.path.join(ARTIFACTS_DIR, "vision3", "split-d-collapsed.png"))
            # Collapsed state survives a navigation rerun (aa TOC cf button).
            detail.get_by_role("button", name="Introduction", exact=True).first.click()
            page.wait_for_url("**marker=Introduction*", timeout=30_000)
            page.wait_for_timeout(800)
            assert rail.bounding_box() is None, "the rail must stay collapsed across a rerun"
            # » restores the rail at its persisted width.
            page.locator(".mdf-split-expand").click()
            page.wait_for_timeout(400)
            w1 = rail.bounding_box()
            assert w1 is not None and abs(w1["width"] - w0) < 3, (
                f"the rail must return at its persisted width: {w0:.0f} -> "
                f"{w1['width'] if w1 else 'hidden'}"
            )
            page.screenshot(path=os.path.join(ARTIFACTS_DIR, "vision3", "split-d-expanded.png"))
        finally:
            browser.close()
            pw.stop()

    _run_in_worker_thread(flow)
