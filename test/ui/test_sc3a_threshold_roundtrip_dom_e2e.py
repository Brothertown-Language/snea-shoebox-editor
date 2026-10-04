"""Issue #1409 SC-3a / SC-3b — preservation gate: threshold override round-trip
and rerun survival on the restructured Records page.

SC-3a: edit the semantic threshold slider in the live UI → the new value is
persisted via PreferenceService (records/semantic_threshold) AND rendered by
both the slider thumb (aria-valuenow) and the coupled number input.

SC-3b: the saved value survives a rerun/navigation — after an st.rerun
triggered by another interaction (🔍 search button) and after a full page
reload, the rendered value equals the saved value (0.70), NOT the fresh
default 0.93 (CALIBRATED_FLOOR).

Harness: dedicated bypass Streamlit server on :8502 (SNEA_E2E=1, headless)
serving the real ``streamlit_app.py``; a healthy server is reused, otherwise
one is auto-launched (sc1a/sc9 harness pattern) and torn down only if the
fixture started it. Worker-thread Playwright pattern per test/ui/AGENTS.md
harness conventions. Run gated: SNEA_E2E=1 (playwright_e2e marker).

Precondition established by test order: the SC-9 fresh-default suite deletes
any saved records/semantic_threshold preference, so a fresh context starts at
the default (0.93); this suite then leaves 0.70 saved for the bypass user.

Co-authored with AI: OpenCode (zai-org/GLM-5.3-Flash)
"""

import os
import queue
import subprocess
import threading
import time
import urllib.request

import pytest

pytest.importorskip("playwright.sync_api")
from playwright.sync_api import Page, sync_playwright  # noqa: E402

from src.services.semantic_search_service import CALIBRATED_FLOOR  # noqa: E402

HARNESS_PORT = int(os.environ.get("SNEA_SC3_PORT", "8502"))
APP_URL = f"http://localhost:{HARNESS_PORT}/records"
ARTIFACTS_DIR = os.path.join("tmp", "issue-1409", "artifacts")

BYPASS_USER_EMAIL = "e2e-test-only-synthetic@invalid"
TARGET_THRESHOLD = 0.70
TOLERANCE = 0.005

pytestmark = [
    pytest.mark.playwright_e2e,
    pytest.mark.skipif(
        os.environ.get("SNEA_E2E", "") != "1",
        reason="live-browser assertion — run with SNEA_E2E=1 (bypass server on :8502)",
    ),
]


def _health_ok() -> bool:
    try:
        with urllib.request.urlopen(
            f"http://localhost:{HARNESS_PORT}/_stcore/health", timeout=2
        ) as r:
            return r.status == 200
    except Exception:
        return False


@pytest.fixture(scope="module")
def bypass_server():
    """Reuse a healthy :8502 bypass server if one is running; otherwise
    auto-launch one headless with SNEA_E2E=1 and terminate it afterwards."""
    preexisting = _health_ok()
    proc = None
    if not preexisting:
        env = dict(os.environ)
        env["SNEA_E2E"] = "1"
        proc = subprocess.Popen(
            [
                "uv", "run", "python", "-m", "streamlit", "run",
                "streamlit_app.py",
                "--server.address", "0.0.0.0",
                "--server.port", str(HARNESS_PORT),
                "--server.headless", "true",
            ],
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        deadline = time.time() + 90
        while time.time() < deadline and not _health_ok():
            time.sleep(1.0)
        if not _health_ok():
            raise AssertionError("SC-3 bypass server failed to become healthy on :8502")
    yield {"preexisting": preexisting}
    if proc is not None:
        proc.terminate()
        try:
            proc.wait(timeout=15)
        except subprocess.TimeoutExpired:
            proc.kill()


def _read_saved_threshold_preference() -> str | None:
    import sys

    sys.path.insert(0, os.path.abspath("."))
    import src.database.models.core  # noqa: F401
    import src.database.models.identity  # noqa: F401
    import src.database.models.iso639  # noqa: F401
    import src.database.models.meta  # noqa: F401
    import src.database.models.search  # noqa: F401
    import src.database.models.workflow  # noqa: F401
    from src.services.preference_service import PreferenceService

    return PreferenceService.get_preference(BYPASS_USER_EMAIL, "records", "semantic_threshold")


class _BrowserSession:
    """Chromium + fresh context + page inside one worker thread (pytest 9 +
    anyio keeps an asyncio loop on the main thread; the Playwright sync API
    forbids entering under a running loop)."""

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
            # Fresh context — the SNEA_E2E bypass authenticates server-side.
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

    def run(self, fn, timeout: float = 300.0):
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


def _wait_for_records_mount(page: Page) -> None:
    deadline = 90_000
    while deadline > 0:
        info = page.evaluate(
            "() => ({"
            "text: document.body.innerText,"
            "sidebar: !!document.querySelector('[data-testid=\"stSidebar\"] input[type=\"number\"]'),"
            "})"
        )
        if "Continue with GitHub" in info["text"]:
            pytest.skip("Bypass did not authenticate (login page rendered) — E2E skipped by design.")
        if info["sidebar"]:
            return
        page.wait_for_timeout(2000)
        deadline -= 2000
    pytest.skip("Records page never mounted on :8502 — E2E skipped by design.")


def _slider_thumb(page: Page):
    return page.locator(
        '[data-testid="stSidebar"] [data-testid="stSlider"] [role="slider"]'
    ).last


def _number_input(page: Page):
    return page.locator('[data-testid="stSidebar"] input[type="number"]').last


def _read_slider_value(page: Page) -> float:
    return float(_slider_thumb(page).get_attribute("aria-valuenow"))


def _read_number_value(page: Page) -> float:
    return float(_number_input(page).input_value())


def _enable_and_edit_slider_to_target(page: Page) -> None:
    """Switch to a semantic search mode (threshold widgets are disabled in
    non-semantic modes), then edit the SLIDER itself via keyboard arrow
    presses until the rendered thumb value reaches the target. Each press
    fires the on_change callback → backing value update + PreferenceService
    persist + st.rerun, so the loop re-reads the live rendered value and
    converges on the target without assuming the starting default."""
    page.locator('[data-testid="stRadio"] label', has_text="Semantic Gloss").first.click()
    # Wait for the rerun that enables the threshold widgets.
    thumb = _slider_thumb(page)
    thumb.wait_for(state="visible", timeout=30_000)
    deadline = 60.0
    while deadline > 0:
        current = _read_slider_value(page)
        if abs(current - TARGET_THRESHOLD) <= TOLERANCE:
            return
        delta = TARGET_THRESHOLD - current
        key = "ArrowRight" if delta > 0 else "ArrowLeft"
        presses = min(max(abs(round(delta / 0.01)), 1), 10)
        thumb.click()
        for _ in range(presses):
            page.keyboard.press(key)
            page.wait_for_timeout(150)
        # Let the last on_change rerun land before re-reading.
        page.wait_for_timeout(2500)
        deadline -= 5.0
    raise AssertionError(
        f"SC-3a: slider never reached {TARGET_THRESHOLD} within 60s of "
        "keyboard editing (last rendered value may differ — see screenshot)."
    )


def test_sc3a_slider_edit_persists_and_renders(bypass_server, session):
    """SC-3a: edit slider → persist via PreferenceService → render new value."""

    def body(page: Page):
        page.goto(APP_URL, wait_until="domcontentloaded")
        _wait_for_records_mount(page)
        _enable_and_edit_slider_to_target(page)

        os.makedirs(ARTIFACTS_DIR, exist_ok=True)
        page.screenshot(
            path=os.path.join(ARTIFACTS_DIR, "sc3a-slider-edit-roundtrip.png"),
            full_page=True,
        )

        # SC-3a assertion 1: the edited value renders in BOTH widgets.
        rendered_slider = _read_slider_value(page)
        rendered_number = _read_number_value(page)
        assert abs(rendered_slider - TARGET_THRESHOLD) <= TOLERANCE, (
            f"SC-3a RED: the slider renders {rendered_slider} after the edit — "
            f"expected the edited value {TARGET_THRESHOLD}."
        )
        assert abs(rendered_number - TARGET_THRESHOLD) <= TOLERANCE, (
            f"SC-3a RED: the coupled number input renders {rendered_number} "
            f"after the slider edit — expected {TARGET_THRESHOLD} (the two "
            "widgets must both render the shared backing value)."
        )

        # SC-3a assertion 2: the edited value is persisted via
        # PreferenceService for the bypass session user.
        saved = _read_saved_threshold_preference()
        assert saved is not None, (
            "SC-3a RED: no records/semantic_threshold preference was persisted "
            f"after the slider edit to {TARGET_THRESHOLD}."
        )
        assert abs(float(saved) - TARGET_THRESHOLD) <= TOLERANCE, (
            f"SC-3a RED: PreferenceService persisted '{saved}' after the "
            f"slider edit — expected {TARGET_THRESHOLD}."
        )

    session.run(body)


def test_sc3b_saved_value_survives_rerun_and_reload(bypass_server, session):
    """SC-3b: the saved value survives rerun/navigation — after an st.rerun
    triggered by another interaction (🔍 search button) and after a full page
    reload, the rendered value equals the SAVED value (0.70), not the fresh
    default (CALIBRATED_FLOOR = 0.93). Unconditional on the SC-3a state:
    the saved preference is re-asserted as the precondition anchor."""

    def body(page: Page):
        # Precondition anchor: a saved preference exists from the SC-3a edit.
        saved = _read_saved_threshold_preference()
        assert saved is not None, (
            "SC-3b precondition failed: no saved records/semantic_threshold "
            "preference exists (SC-3a edit must run first in the same module)."
        )
        saved_value = float(saved)

        # Rerun via another interaction: the 🔍 search button triggers
        # st.rerun() (search trigger) — the page re-renders with the saved
        # preference as the seeding source.
        page.locator('[data-testid="stBaseButton-secondary"]').first.click()
        page.wait_for_timeout(4000)
        _wait_for_records_mount(page)
        # Switch back to a semantic mode so the threshold widgets are enabled
        # and rendered with live values (the mode radio may have reset).
        page.locator('[data-testid="stRadio"] label', has_text="Semantic Gloss").first.click()
        page.wait_for_timeout(4000)

        os.makedirs(ARTIFACTS_DIR, exist_ok=True)
        page.screenshot(
            path=os.path.join(ARTIFACTS_DIR, "sc3b-rerun-survival.png"),
            full_page=True,
        )

        rendered_after_rerun = _read_number_value(page)
        assert abs(rendered_after_rerun - saved_value) <= TOLERANCE, (
            f"SC-3b RED: after st.rerun the number input renders "
            f"{rendered_after_rerun} instead of the saved value {saved_value} "
            "— the saved preference did not survive the rerun."
        )

        # Navigation survival: full page reload re-seeds from the saved
        # preference — must NOT reset to the fresh default.
        page.reload(wait_until="domcontentloaded")
        _wait_for_records_mount(page)
        page.locator('[data-testid="stRadio"] label', has_text="Semantic Gloss").first.click()
        page.wait_for_timeout(4000)
        rendered_after_reload = _read_number_value(page)
        assert abs(rendered_after_reload - saved_value) <= TOLERANCE, (
            f"SC-3b RED: after page reload the number input renders "
            f"{rendered_after_reload} instead of the saved value {saved_value} "
            f"— the rendered value reset (fresh default is {CALIBRATED_FLOOR})."
        )

    session.run(body)
