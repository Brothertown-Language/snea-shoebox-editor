"""Issue #1401 SC-15 — Playwright real-browser computed-style assertion:
``mark.search-token`` background-color is DISTINCT from the computed
background-colors of ``mark.diff-token`` marks and of the tinted status
lines, in BOTH theme variants (light and dark emulation via
``page.emulate_media(color_scheme=...)``), and the search-token styling is
theme-variant (the light-variant computed background-color differs from the
dark-variant computed background-color).

Drives a real Chromium against a harness page (test/ui/fixtures/
sc15_theme_variant_harness.py, served by Streamlit on a dedicated port) that
renders the MDF block renderer with active search-token highlighting PLUS
diff-token spans PLUS the full tinted status-line set — so all three
compared element classes are present in the block DOM simultaneously and the
distinctness assertion targets the SC-15 styling itself and cannot fail for
wiring reasons (page wiring is SC-17, out of scope here). Reuses the
SC-13/SC-14 harness pattern.

Pre-GREEN (the search-token CSS in ``src/frontend/ui_utils.py`` is a single
static color with no ``@media (prefers-color-scheme: ...)`` variants —
verified live 2026-10-02) the gate-enabled run MUST FAIL at the
theme-variant assertion. Without the gate the test records SKIPPED by
design — plain ``pytest test/`` stays green serverless. The harness
subprocess is managed by the test itself (launched headless, torn down
after the run).

Worker-thread pattern per test/ui/AGENTS.md harness conventions.

Co-authored with AI: OpenCode (GLM-5.3-Flash)
"""

import os
import queue
import subprocess
import threading
import time
import urllib.request

import pytest
from playwright.sync_api import Page, sync_playwright

HARNESS_PORT = int(os.environ.get("SNEA_SC15_PORT", "8504"))
APP_URL = f"http://localhost:{HARNESS_PORT}/"
ARTIFACTS_DIR = os.path.join("tmp", "issue-1401", "artifacts")

pytest.importorskip("playwright.sync_api")

pytestmark = [
    pytest.mark.playwright_e2e,
    pytest.mark.skipif(
        os.environ.get("SNEA_E2E", "") != "1",
        reason="live-browser assertion — run with SNEA_E2E=1 (harness auto-launched)",
    ),
]

# Status classes with defined tint CSS in src/frontend/ui_utils.py
# (status-ok is unstyled and excluded).
TINTED_STATUS_SELECTOR = (
    '.mdf-line.status-suggestion, .mdf-line.status-note, .mdf-line.status-error,'
    ' .mdf-line.status-warning, .mdf-line.status-diff-changed,'
    ' .mdf-line.status-diff-added, .mdf-line.status-diff-removed'
)


@pytest.fixture(scope="module")
def harness():
    """Launch the SC-15 harness Streamlit page headless and wait for health."""
    proc = subprocess.Popen(
        [
            "uv", "run", "python", "-m", "streamlit", "run",
            "test/ui/fixtures/sc15_theme_variant_harness.py",
            "--server.address", "0.0.0.0",
            "--server.port", str(HARNESS_PORT),
            "--server.headless", "true",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        deadline = time.time() + 60
        healthy = False
        while time.time() < deadline:
            try:
                with urllib.request.urlopen(
                    f"http://localhost:{HARNESS_PORT}/_stcore/health", timeout=2
                ) as r:
                    if r.status == 200:
                        healthy = True
                        break
            except Exception:
                time.sleep(1.0)
        if not healthy:
            raise AssertionError("SC-15 harness failed to become healthy on :%d" % HARNESS_PORT)
        yield
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=15)
        except subprocess.TimeoutExpired:
            proc.kill()


class _BrowserSession:
    """Chromium + page inside one worker thread (pytest 9 + anyio keeps an
    asyncio loop on the main thread; the Playwright sync API forbids entering
    under a running loop)."""

    def __init__(self):
        self._jobs: queue.Queue = queue.Queue()
        self._result_box: list[BaseException | None] = []
        self._done_evt = threading.Event()
        self._ready_evt = threading.Event()
        self._shutdown = threading.Event()
        self.thread = threading.Thread(target=self._main, daemon=True)
        self.thread.start()
        self._ready_evt.wait(timeout=60)

    def _main(self):
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            page = browser.new_context().new_page()
            self._ready_evt.set()
            while not self._shutdown.is_set():
                try:
                    fn = self._jobs.get(timeout=0.2)
                except queue.Empty:
                    continue
                if fn is None:
                    break
                self._result_box.clear()
                try:
                    fn(page)
                    self._result_box.append(None)
                except BaseException as e:  # noqa: BLE001 — propagate verbatim
                    self._result_box.append(e)
                self._done_evt.set()
            browser.close()

    def run(self, fn, timeout: float = 180.0):
        self._done_evt.clear()
        self._jobs.put(fn)
        if not self._done_evt.wait(timeout=timeout):
            raise TimeoutError(f"test body exceeded {timeout}s in worker thread")
        err = self._result_box[0] if self._result_box else RuntimeError("worker returned no result")
        if err is not None:
            raise err

    def close(self):
        self._shutdown.set()
        self._jobs.put(None)
        self.thread.join(timeout=30)


@pytest.fixture(scope="module")
def session():
    sess = _BrowserSession()
    yield sess
    sess.close()


def _collect_bg_colors(page: Page) -> dict:
    """Computed background-colors of search-token marks, diff-token marks,
    and tinted status lines from the main document. Verified live (Streamlit
    1.54): st.html renders INLINE in the main document — no iframes."""
    return page.evaluate(
        """statusSel => {
        const grab = sel => [...document.querySelectorAll(sel)].map(
            el => getComputedStyle(el).backgroundColor);
        const status = {};
        for (const el of document.querySelectorAll(statusSel)) {
            const cls = [...el.classList].find(c => c.startsWith('status-')) || 'unknown';
            const bg = getComputedStyle(el).backgroundColor;
            (status[cls] = status[cls] || []).push(bg);
        }
        for (const k of Object.keys(status)) status[k].sort();
        return {
            searchTokens: grab('.mdf-wrap-block mark.search-token'),
            diffTokens: grab('.mdf-wrap-block mark.diff-token'),
            statusTints: status,
        };
    }""",
        TINTED_STATUS_SELECTOR,
    )


def _sc15_flow(page: Page):
    variants: dict[str, dict] = {}
    for theme in ("light", "dark"):
        page.emulate_media(color_scheme=theme)
        page.goto(APP_URL, wait_until="domcontentloaded")
        page.wait_for_function(
            "() => document.querySelectorAll('.mdf-wrap-block').length >= 1",
            timeout=45_000,
        )
        page.wait_for_timeout(1000)
        variants[theme] = _collect_bg_colors(page)
        page.screenshot(path=os.path.join(ARTIFACTS_DIR, f"sc15-harness-{theme}.png"))

    for theme in ("light", "dark"):
        v = variants[theme]

        # Assertion 1 (harness precondition): all three compared element
        # classes must be present in the block DOM.
        assert v["searchTokens"], (
            f"SC-15 ({theme}): no mark.search-token in the harness-rendered "
            "MDF block DOM — the highlight-wrap deliverable (SC-10) is not "
            "producing marks, so distinctness cannot be asserted."
        )
        assert v["diffTokens"], (
            f"SC-15 ({theme}): no mark.diff-token in the harness-rendered "
            "MDF block DOM — the diff-token comparison baseline is missing."
        )
        assert v["statusTints"], (
            f"SC-15 ({theme}): no tinted status lines in the harness-rendered "
            "MDF block DOM — the status-tint comparison baseline is missing."
        )

        # Assertion 2 (the SC-15 target): search-token bg differs from
        # diff-token bg and from every status-line tint in this variant.
        search_bgs = sorted(set(v["searchTokens"]))
        diff_bgs = sorted(set(v["diffTokens"]))
        collisions = []
        for sb in search_bgs:
            if sb in diff_bgs:
                collisions.append(f"search-token bg {sb} == diff-token bg")
            for cls, tints in sorted(v["statusTints"].items()):
                if sb in tints:
                    collisions.append(f"search-token bg {sb} == {cls} tint")
        assert not collisions, (
            f"SC-15 RED ({theme}): mark.search-token background-color is NOT "
            "distinct from diff-token marks / status line tints — "
            + "; ".join(collisions)
        )

    # Assertion 3 (theme-variant styles): light and dark variants of the
    # search-token styling must produce different computed background-colors.
    light_bgs = sorted(set(variants["light"]["searchTokens"]))
    dark_bgs = sorted(set(variants["dark"]["searchTokens"]))
    assert set(light_bgs) != set(dark_bgs), (
        "SC-15 RED: search-token computed background-color is identical in "
        f"light ({light_bgs}) and dark ({dark_bgs}) emulation — no "
        "theme-variant styles defined for mark.search-token."
    )


def test_sc15_search_token_distinct_in_both_theme_variants(harness, session):
    session.run(_sc15_flow)


def test_sc15_gate_absent_variant_skips_by_design(harness, session):
    """Gate-absent variant: without SNEA_E2E=1 this test (and the gated SC-15
    suite) is SKIPPED BY DESIGN — never silently treated as a pass. With the
    gate present it verifies the harness precondition the gated run relies
    on (health endpoint 200)."""
    if os.environ.get("SNEA_E2E", "") != "1":
        pytest.skip(
            "SC-15 gate-absent variant: skipped by design — live-browser "
            "assertion requires SNEA_E2E=1 (harness auto-launched)"
        )

    def _health(page: Page):
        page.goto(f"http://localhost:{HARNESS_PORT}/_stcore/health", wait_until="domcontentloaded")
        body = page.locator("body").inner_text()
        assert "ok" in body.lower(), f"SC-15: harness health not ok: {body!r}"

    session.run(_health)