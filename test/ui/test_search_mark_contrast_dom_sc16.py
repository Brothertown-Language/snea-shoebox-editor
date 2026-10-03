"""Issue #1401 SC-16 — Playwright real-browser WCAG contrast-ratio assertion:
the contrast ratio between ``mark.search-token``'s effective text color and
its effective composited background (semi-transparent mark background alpha-
composited over the underlying block background) must be >= 4.5:1 (WCAG 2.1
AA normal text) in BOTH theme variants (light and dark emulation via
``page.emulate_media(color_scheme=...)``).

The ratio is computed IN-BROWSER from live computed styles: the WCAG 2.1
relative-luminance formula applied to the sRGB channels of the mark's text
color and of the mark background alpha-composited over the ancestor
background chain (per CSS alpha compositing), so the measurement reflects the
actually rendered pixels rather than the authored rgba constants.

Drives a real Chromium against a harness page (test/ui/fixtures/
sc16_contrast_harness.py, served by Streamlit on a dedicated port) that
renders the MDF block renderer with active search-token highlighting — so
the assertion targets the SC-16 styling itself and cannot fail for wiring
reasons. Reuses the SC-13/SC-14/SC-15 harness pattern.

Pre-GREEN (the mark uses ``color: inherit`` with rgba teal backgrounds —
rgba(0,160,170,0.35) light / rgba(0,190,200,0.5) dark — verified in
``src/frontend/ui_utils.py``) the gate-enabled run MUST FAIL if the measured
ratio is below 4.5:1 in either theme. If measurement shows the ratio already
>= 4.5:1 in both themes, the test PASSES and the computed ratios are recorded
as ALREADY_GREEN evidence. Without the gate the test records SKIPPED by
design — plain ``pytest test/`` stays green serverless. The harness
subprocess is managed by the test itself (launched headless, torn down after
the run).

Worker-thread pattern per test/ui/AGENTS.md harness conventions.

Co-authored with AI: OpenCode (GLM-5.3-Flash)
"""

import json
import os
import queue
import subprocess
import threading
import time
import urllib.request

import pytest
from playwright.sync_api import Page, sync_playwright

HARNESS_PORT = int(os.environ.get("SNEA_SC16_PORT", "8505"))
APP_URL = f"http://localhost:{HARNESS_PORT}/"
ARTIFACTS_DIR = os.path.join("tmp", "issue-1401", "artifacts")
WCAG_AA_NORMAL_TEXT_RATIO = 4.5

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
    """Launch the SC-16 harness Streamlit page headless and wait for health."""
    proc = subprocess.Popen(
        [
            "uv", "run", "python", "-m", "streamlit", "run",
            "test/ui/fixtures/sc16_contrast_harness.py",
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
            raise AssertionError(f"SC-16 harness failed to become healthy on :{HARNESS_PORT}")
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


# In-browser measurement: WCAG 2.1 relative luminance + alpha compositing.
# For each mark.search-token we read the computed text color and background
# color, then alpha-composite the mark background over the ancestor
# background chain (bottom-most opaque layer as base) exactly as the browser
# composites it when painting, then compute (L1+0.05)/(L2+0.05).
_MEASURE_JS = """
() => {
    const parseColor = (s) => {
        const m = s.match(/rgba?\\(([\\d.]+),\\s*([\\d.]+),\\s*([\\d.]+)(?:,\\s*([\\d.]+))?\\)/);
        if (!m) throw new Error('unparseable color: ' + s);
        return [parseFloat(m[1]), parseFloat(m[2]), parseFloat(m[3]),
                m[4] === undefined ? 1 : parseFloat(m[4])];
    };
    const linearize = (c) => {
        const v = c / 255;
        return v <= 0.04045 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
    };
    const luminance = ([r, g, b]) =>
        0.2126 * linearize(r) + 0.7152 * linearize(g) + 0.0722 * linearize(b);
    // Composite fg OVER bg (both [r,g,b,a] in 0-255 / 0-1).
    const composite = (fg, bg) => {
        const a = fg[3];
        return [
            fg[0] * a + bg[0] * (1 - a),
            fg[1] * a + bg[1] * (1 - a),
            fg[2] * a + bg[2] * (1 - a),
            a + bg[3] * (1 - a),
        ];
    };
    const contrast = (l1, l2) => {
        const [hi, lo] = l1 >= l2 ? [l1, l2] : [l2, l1];
        return (hi + 0.05) / (lo + 0.05);
    };

    const marks = [...document.querySelectorAll('.mdf-wrap-block mark.search-token')];
    if (!marks.length) return { error: 'no mark.search-token found' };

    const results = [];
    for (const mark of marks) {
        const markStyle = getComputedStyle(mark);
        const textColor = parseColor(markStyle.color);   // color:inherit resolved

        // Walk the ancestor chain gathering background layers bottom-up.
        const layers = [];  // [{color, el}] top DOM -> bottom
        let el = mark.parentElement;
        while (el) {
            const bg = parseColor(getComputedStyle(el).backgroundColor);
            if (bg[3] > 0) layers.push(bg);
            if (bg[3] >= 1) break;  // opaque base found — stop
            el = el.parentElement;
        }
        if (!layers.length || layers[layers.length - 1][3] < 1) {
            return { error: 'no opaque ancestor background found under mark' };
        }
        // Composite top-down: start from the bottom-most layer, apply each
        // layer above it (last array element is the bottom-most).
        let composited = layers[layers.length - 1];
        for (let i = layers.length - 2; i >= 0; i--) {
            composited = composite(layers[i], composited);
        }
        // Mark background is the topmost layer.
        const markBg = parseColor(markStyle.backgroundColor);
        const effectiveBg = composite(markBg, composited);

        const lText = luminance(textColor);
        const lBg = luminance(effectiveBg);
        results.push({
            textColor: markStyle.color,
            markBg: markStyle.backgroundColor,
            effectiveBg: effectiveBg.map(v => Math.round(v * 100) / 100).join(','),
            ratio: Math.round(contrast(lText, lBg) * 100) / 100,
        });
    }
    return results;
}
"""


def _sc16_flow(page: Page) -> dict:
    variants: dict[str, list[dict]] = {}
    for theme in ("light", "dark"):
        page.emulate_media(color_scheme=theme)
        page.goto(APP_URL, wait_until="domcontentloaded")
        page.wait_for_function(
            "() => document.querySelectorAll('.mdf-wrap-block').length >= 1",
            timeout=45_000,
        )
        page.wait_for_function(
            "() => document.querySelectorAll('.mdf-wrap-block mark.search-token').length >= 1",
            timeout=45_000,
        )
        page.wait_for_timeout(1000)
        variants[theme] = page.evaluate(_MEASURE_JS)
        page.screenshot(path=os.path.join(ARTIFACTS_DIR, f"sc16-contrast-{theme}.png"))

    measurements = {"theme": dict(variants)}
    with open(
        os.path.join(ARTIFACTS_DIR, "sc16-contrast-measurements.json"), "w"
    ) as f:
        json.dump(measurements, f, indent=2)

    for theme in ("light", "dark"):
        data = variants[theme]
        assert not (isinstance(data, dict) and "error" in data), (
            f"SC-16 ({theme}): in-browser measurement failed: {data.get('error')}"
        )
        assert data, f"SC-16 ({theme}): no mark.search-token measurements returned"
        for m in data:
            assert m["ratio"] >= WCAG_AA_NORMAL_TEXT_RATIO, (
                f"SC-16 RED ({theme}): mark.search-token contrast ratio "
                f"{m['ratio']}:1 is below the WCAG 2.1 AA normal-text "
                f"threshold of {WCAG_AA_NORMAL_TEXT_RATIO}:1 "
                f"(text {m['textColor']} over effective composited bg "
                f"rgb({m['effectiveBg']}), mark bg {m['markBg']})"
            )
    return measurements


def test_sc16_search_token_contrast_aa_both_theme_variants(harness, session):
    session.run(_sc16_flow)


def test_sc16_gate_absent_variant_skips_by_design(harness, session):
    """Gate-absent variant: without SNEA_E2E=1 this test (and the gated SC-16
    suite) is SKIPPED BY DESIGN — never silently treated as a pass. With the
    gate present it verifies the harness precondition the gated run relies
    on (health endpoint 200)."""
    if os.environ.get("SNEA_E2E", "") != "1":
        pytest.skip(
            "SC-16 gate-absent variant: skipped by design — live-browser "
            "assertion requires SNEA_E2E=1 (harness auto-launched)"
        )

    def _health(page: Page):
        page.goto(f"http://localhost:{HARNESS_PORT}/_stcore/health", wait_until="domcontentloaded")
        body = page.locator("body").inner_text()
        assert "ok" in body.lower(), f"SC-16: harness health not ok: {body!r}"

    session.run(_health)
