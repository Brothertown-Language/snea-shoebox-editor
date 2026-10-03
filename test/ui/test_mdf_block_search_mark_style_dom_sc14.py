"""Issue #1401 SC-14 — Playwright real-browser computed-style assertion:
``mark.search-token`` marks render with the defined teal/cyan background
tint AND bold font weight.

Drives a real Chromium against a harness page (test/ui/fixtures/
sc14_search_token_style_harness.py, served by Streamlit on a dedicated port)
that renders the MDF block renderer with active search-token highlighting —
``mark.search-token`` elements are present in the block DOM (the wrap logic
is SC-10's deliverable and already exists in ``src/frontend/ui_utils.py``),
so the computed-style assertion targets the SC-14 styling itself and cannot
fail for wiring reasons (page wiring is SC-17, out of scope here).

Assertion: every ``mark.search-token`` computed style has (a) a background
color that is NOT fully transparent and whose hue falls in the teal/cyan
band (~150°-210°), and (b) a bold font weight (>= 700).

Pre-GREEN (no ``mark.search-token`` CSS block exists in
``src/frontend/ui_utils.py`` — only ``mark.diff-token`` styles are defined)
the gate-enabled run MUST FAIL: marks render with UA default styling
(opaque yellow, normal weight). Without the gate the test records SKIPPED
by design — plain ``pytest test/`` stays green serverless. The harness
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

HARNESS_PORT = int(os.environ.get("SNEA_SC14_PORT", "8503"))
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


@pytest.fixture(scope="module")
def harness():
    """Launch the SC-14 harness Streamlit page headless and wait for health."""
    proc = subprocess.Popen(
        [
            "uv", "run", "python", "-m", "streamlit", "run",
            "test/ui/fixtures/sc14_search_token_style_harness.py",
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
            raise AssertionError("SC-14 harness failed to become healthy on :8503")
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


def _collect_mark_styles(page: Page) -> list[dict]:
    """Computed background-color (rgba) + font-weight of every rendered
    mark.search-token. Verified live (Streamlit 1.54): st.html renders
    INLINE in the main document — no iframes."""
    return page.evaluate(
        """() => {
        const out = [];
        for (const el of document.querySelectorAll('.mdf-wrap-block mark.search-token')) {
            const cs = getComputedStyle(el);
            out.push({
                backgroundColor: cs.backgroundColor,
                fontWeight: cs.fontWeight,
                color: cs.color,
            });
        }
        return out;
    }"""
    )


def _hue_of(bg: str) -> float:
    """Hue in degrees (0-360) of an rgb()/rgba() string; -1.0 when
    transparent/achromatic/unparseable."""
    parts = bg.replace("rgba(", "").replace("rgb(", "").rstrip(")").split(",")
    if len(parts) < 3:
        return -1.0
    try:
        r, g, b = (float(p) for p in parts[:3])
    except ValueError:
        return -1.0
    alpha = float(parts[3]) if len(parts) == 4 else 1.0
    if alpha <= 0 or max(r, g, b) <= 0:
        return -1.0
    mx, mn = max(r, g, b), min(r, g, b)
    d = mx - mn
    if d == 0:
        return -1.0
    if mx == r:
        return (60 * ((g - b) / d)) % 360
    if mx == g:
        return 60 * ((b - r) / d) + 120
    return 60 * ((r - g) / d) + 240


def _sc14_flow(page: Page):
    page.goto(APP_URL, wait_until="domcontentloaded")
    page.wait_for_function(
        """() => document.querySelectorAll('.mdf-wrap-block').length >= 1""",
        timeout=45_000,
    )
    page.wait_for_timeout(1000)

    styles = _collect_mark_styles(page)
    page.screenshot(path=os.path.join(ARTIFACTS_DIR, "sc14-harness-search-tokens.png"))

    # Assertion 1 (wiring precondition from SC-10): marks must render.
    assert styles, (
        "SC-14: no mark.search-token in the harness-rendered MDF block DOM — "
        "the highlight-wrap deliverable (SC-10) is not producing marks, so "
        "the computed-style assertion cannot target the SC-14 styling."
    )

    # Assertion 2 (the SC-14 target): teal/cyan background tint + bold weight.
    failures = []
    for i, style in enumerate(styles):
        bg = style["backgroundColor"]
        weight = style["fontWeight"]
        hue = _hue_of(bg)
        # Teal/cyan band: hue 150-210 (green-cyan through blue-cyan).
        if not (150 <= hue <= 210):
            failures.append(
                f"mark[{i}] background-color={bg!r} hue={hue:.0f} not teal/cyan"
            )
        try:
            numeric_weight = float(weight)
        except ValueError:
            numeric_weight = 400.0
        if numeric_weight < 700:
            failures.append(
                f"mark[{i}] font-weight={weight!r} not bold (>=700)"
            )

    assert not failures, (
        "SC-14 RED: mark.search-token computed styles do not match the "
        "defined teal/cyan background tint plus bold font weight — the CSS "
        "block is missing from src/frontend/ui_utils.py: " + "; ".join(failures)
    )


def test_sc14_search_token_computed_style(harness, session):
    session.run(_sc14_flow)


def test_sc14_gate_absent_variant_skips_by_design(harness, session):
    """Gate-absent variant: without SNEA_E2E=1 this test (and the gated SC-14
    suite) is SKIPPED BY DESIGN — never silently treated as a pass. With the
    gate present it verifies the harness precondition the gated run relies
    on (health endpoint 200)."""
    if os.environ.get("SNEA_E2E", "") != "1":
        pytest.skip(
            "SC-14 gate-absent variant: skipped by design — live-browser "
            "assertion requires SNEA_E2E=1 (harness auto-launched)"
        )

    def _health(page: Page):
        page.goto(f"http://localhost:{HARNESS_PORT}/_stcore/health", wait_until="domcontentloaded")
        body = page.locator("body").inner_text()
        assert "ok" in body.lower(), f"SC-14: harness health not ok: {body!r}"

    session.run(_health)