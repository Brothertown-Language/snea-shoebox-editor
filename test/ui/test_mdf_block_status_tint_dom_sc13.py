"""Issue #1401 SC-13 — Playwright real-browser DOM + computed-style assertion:
status line tints render UNCHANGED when search-token highlighting is active.

Drives a real Chromium against a harness page (test/ui/fixtures/
sc13_status_tint_harness.py, served by Streamlit on a dedicated port) that
renders the MDF block renderer twice with identical status-line diagnostics:
once without highlight spans and once with active search-token highlighting.
For each diagnostics status class, the computed ``background-color`` and
``border-left-color`` of the ``.mdf-line`` div must be identical in both
renders, and the highlighted render must actually contain
``mark.search-token`` marks (so the comparison is not vacuous).

Gated by the ``playwright_e2e`` marker + ``SNEA_E2E=1``; plain ``pytest
test/`` stays green serverless. The harness subprocess is managed by the
test itself (launched headless, torn down after the run).

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

HARNESS_PORT = int(os.environ.get("SNEA_SC13_PORT", "8502"))
APP_URL = f"http://localhost:{HARNESS_PORT}/"
ARTIFACTS_DIR = os.path.join("tmp", "issue-1401", "artifacts")

STATUS_CLASSES = [
    "status-ok",
    "status-note",
    "status-warning",
    "status-suggestion",
    "status-error",
    "status-diff-changed",
    "status-diff-added",
    "status-diff-removed",
]

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
    """Launch the SC-13 harness Streamlit page headless and wait for health."""
    proc = subprocess.Popen(
        [
            "uv", "run", "python", "-m", "streamlit", "run",
            "test/ui/fixtures/sc13_status_tint_harness.py",
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
            raise AssertionError("SC-13 harness failed to become healthy on :8502")
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


def _collect_block_tints(page: Page) -> dict:
    """For every .mdf-wrap-block in the main document, collect per-status
    computed background-color / border-left-color and search-token count."""
    return page.evaluate(
        """(statusClasses) => {
        const blocks = [];
        for (const block of document.querySelectorAll('.mdf-wrap-block')) {
            const tints = {};
            for (const cls of statusClasses) tints[cls] = new Set();
            let marks = 0;
            for (const line of block.querySelectorAll('.mdf-line')) {
                for (const cls of line.className.split(/\\s+/)) {
                    if (statusClasses.includes(cls)) {
                        const cs = getComputedStyle(line);
                        tints[cls].add(cs.backgroundColor + '|' + cs.borderLeftColor);
                    }
                }
            }
            marks = block.querySelectorAll('mark.search-token').length;
            const out = {marks, tints: {}};
            for (const cls of statusClasses) out.tints[cls] = [...tints[cls]];
            blocks.push(out);
        }
        return blocks;
    }""",
        STATUS_CLASSES,
    )


def _sc13_flow(page: Page):
    page.goto(APP_URL, wait_until="domcontentloaded")
    page.wait_for_function(
        """() => document.querySelectorAll('.mdf-wrap-block').length >= 2""",
        timeout=45_000,
    )
    page.wait_for_timeout(1000)

    blocks = _collect_block_tints(page)
    page.screenshot(path=os.path.join(ARTIFACTS_DIR, "sc13-harness-tints.png"))

    baseline, active = blocks[0], blocks[1]

    # Preconditions: the highlighted render actually contains search-token
    # marks — otherwise the tint comparison does not exercise SC-13.
    assert active["marks"] > 0, (
        "SC-13: the highlighted render contains no mark.search-token — "
        "highlighting is not active, so the tint comparison is vacuous."
    )

    # SC-13 assertion: for every status class present in both renders, the
    # computed tint (background-color | border-left-color) is IDENTICAL with
    # and without active highlighting.
    failures = []
    for cls in STATUS_CLASSES:
        base_set = set(baseline["tints"][cls])
        act_set = set(active["tints"][cls])
        if not base_set and not act_set:
            continue  # status class not exercised by the harness
        if not base_set or not act_set:
            failures.append(f"{cls}: present in only one render (base={base_set}, active={act_set})")
        elif base_set != act_set:
            failures.append(f"{cls}: tint changed — base={base_set}, active={act_set}")

    assert not failures, (
        "SC-13 RED: status line tints changed when search-token highlighting "
        f"became active: {failures}"
    )


def test_sc13_status_tints_unchanged_with_highlighting(harness, session):
    session.run(_sc13_flow)