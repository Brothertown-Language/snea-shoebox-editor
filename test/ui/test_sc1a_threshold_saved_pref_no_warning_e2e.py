"""Issue #1409 SC-1a — RED: a SAVED records/semantic_threshold preference must
NOT trigger a Streamlit widget-state warning box on the Records page.

SC-1a: with a saved ``records``/``semantic_threshold`` preference (e.g. 0.85)
for the bypass session user, the rendered Records page must contain NO
Streamlit widget-state warning box for the semantic threshold widgets.

RED state (2026-10-03): ``src/frontend/pages/records.py`` lines 412-419 write
``st.session_state.semantic_threshold_slider``/``..._number`` pre-instantiation
from the saved preference, then instantiate the widgets with an explicit
``value=`` (lines 440/453) — Streamlit emits the dual-set warning
"... was created with a default value but also had its value set via the
Session State API", so the assertion below FAILS against the current tree.

Harness: dedicated bypass Streamlit server on :8502 (SNEA_E2E=1, headless)
serving the real ``streamlit_app.py``; server auto-launched by the module
fixture if none is healthy (sc13 harness pattern) and torn down only if the
fixture started it. Seeding is scoped INSIDE this test file (no use of the
``_delete_saved_threshold_preferences`` fixture, which would erase the saved
preference this SC depends on).

Worker-thread Playwright pattern per test/ui/AGENTS.md harness conventions.

Co-authored with AI: OpenCode (zai-org/GLM-5.3-Flash)
"""

import os
import queue
import subprocess
import threading
import time
import urllib.request

import pytest

HARNESS_PORT = int(os.environ.get("SNEA_SC1A_PORT", "8502"))
APP_URL = f"http://localhost:{HARNESS_PORT}/records"
ARTIFACTS_DIR = os.path.join("tmp", "issue-1409", "artifacts")

BYPASS_USER_EMAIL = "e2e-test-only-synthetic@invalid"
SAVED_THRESHOLD = "0.85"

# Streamlit's dual-set warning text fragment (stable across recent versions).
WARNING_FRAGMENT = "Session State API"

pytest.importorskip("playwright.sync_api")
from playwright.sync_api import Page, sync_playwright  # noqa: E402

pytestmark = [
    pytest.mark.playwright_e2e,
    pytest.mark.skipif(
        os.environ.get("SNEA_E2E", "") != "1",
        reason="live-browser assertion — run with SNEA_E2E=1 (bypass server auto-launched on :8502)",
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
            raise AssertionError("SC-1a bypass server failed to become healthy on :8502")
    # Seed the saved preference BEFORE any browser page load: Streamlit's
    # _shown_default_value_warning is a once-per-process module global, so the
    # first script run is the only run that can render the warning. The
    # seeded preference must be in place for that first run (bare-mode
    # IdentityService.sync_user_to_db is script-context-independent — it was
    # only gated on ctx inside security_manager.py's bypass hook).
    _seed_saved_threshold_preference()
    assert _read_saved_threshold_preference() == SAVED_THRESHOLD, (
        "Precondition failed: saved records/semantic_threshold preference "
        f"was not seeded as {SAVED_THRESHOLD}."
    )
    yield {"preexisting": preexisting}
    if proc is not None:
        proc.terminate()
        try:
            proc.wait(timeout=15)
        except subprocess.TimeoutExpired:
            proc.kill()


def _seed_saved_threshold_preference() -> None:
    """Seed the saved records/semantic_threshold preference (0.85) for the
    bypass session user via PreferenceService (test fixture data, same
    identity the SNEA_E2E bypass establishes)."""
    import sys

    sys.path.insert(0, os.path.abspath("."))
    # Register all SQLAlchemy mappers first (helper precedent:
    # test_sc9_ui_threshold_default_red.py::_delete_saved_threshold_preferences).
    import src.database.models.core  # noqa: F401
    import src.database.models.identity  # noqa: F401
    import src.database.models.iso639  # noqa: F401
    import src.database.models.meta  # noqa: F401
    import src.database.models.search  # noqa: F401
    import src.database.models.workflow  # noqa: F401
    from src.services.identity_service import (
        _SIMULATED_USER_INFO,
        IdentityService,
    )
    from src.services.preference_service import PreferenceService

    # Ensure the FK-backed user row exists for the bypass identity (idempotent,
    # mirrors security_manager.py's bypass seeding).
    IdentityService.sync_user_to_db(_SIMULATED_USER_INFO, BYPASS_USER_EMAIL)
    PreferenceService.set_preference(
        BYPASS_USER_EMAIL, "records", "semantic_threshold", SAVED_THRESHOLD
    )


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


def _poll_for_widget_warning(page: Page) -> bool:
    """Poll the DOM (CDP DOMSnapshot — st.warning text lives inside closed
    shadow roots invisible to innerText) from the earliest possible moment
    of the load and report whether the dual-set widget-state warning ever
    renders. The warning is TRANSIENT on the live app: it renders during the
    first script run and is wiped by the follow-up rerun (Streamlit's
    once-per-process _shown_default_value_warning flag), so a post-mount
    innerText check is vacuous — polling during the load window is required."""
    cdp = page.context.new_cdp_session(page)
    deadline = 40.0
    while deadline > 0:
        try:
            snap = cdp.send("DOMSnapshot.captureSnapshot", {"computedStyles": []})
            if any(WARNING_FRAGMENT in s for s in snap["strings"]):
                return True
        except Exception:
            pass
        page.wait_for_timeout(100)
        deadline -= 0.1
    return False


def _sc1a_flow(page: Page):
    # Seeding is scoped to this test file (fixture-level, BEFORE the first
    # page load) — the existing _delete_saved_threshold_preferences fixture
    # is NOT used. Single load: the first script run of the server process is
    # the only one that can render the once-per-process dual-set warning, so
    # the polling must cover this load from the earliest possible moment.
    page.goto(APP_URL, wait_until="commit")
    warning_seen = _poll_for_widget_warning(page)
    _wait_for_records_mount(page)

    os.makedirs(ARTIFACTS_DIR, exist_ok=True)
    page.screenshot(
        path=os.path.join(ARTIFACTS_DIR, "sc1a-saved-pref-no-warning.png"),
        full_page=True,
    )

    # Precondition: the saved preference actually drives the widget (the
    # sidebar numeric input shows 0.85), so the warning check is not vacuous.
    number = page.locator('[data-testid="stSidebar"] input[type="number"]').last
    rendered = float(number.input_value())
    assert abs(rendered - float(SAVED_THRESHOLD)) <= 0.005, (
        f"Precondition failed: saved preference {SAVED_THRESHOLD} did not "
        f"drive the rendered threshold widget (rendered {rendered})."
    )

    # SC-1b assertion: the slider itself renders the saved value 0.85 —
    # read the ACTUAL rendered value from the DOM (aria-valuenow on the
    # slider thumb role), not just the pre-render gate.
    slider_thumb = page.locator(
        '[data-testid="stSidebar"] [data-testid="stSlider"] [role="slider"]'
    ).last
    slider_rendered = float(slider_thumb.get_attribute("aria-valuenow"))
    assert abs(slider_rendered - float(SAVED_THRESHOLD)) <= 0.005, (
        f"SC-1b RED: the threshold slider rendered {slider_rendered} instead "
        f"of the saved records/semantic_threshold preference {SAVED_THRESHOLD}."
    )

    # SC-1a assertion: NO Streamlit widget-state warning box for the threshold
    # widgets may appear at any point while the page loads with a saved
    # preference present.
    assert not warning_seen, (
        "SC-1a RED: the Records page rendered a Streamlit widget-state "
        "warning box ('... was created with a default value but also had "
        f"its value set via the {WARNING_FRAGMENT} ...') while a saved "
        f"records/semantic_threshold preference ({SAVED_THRESHOLD}) exists — "
        "root cause: records.py pre-instantiation session_state writes "
        "(lines 412-419) combined with value= on the widget constructors "
        "(lines 440/453) trigger the dual-set warning."
    )


def test_sc1a_saved_threshold_pref_renders_no_widget_warning(bypass_server, session):
    session.run(_sc1a_flow)
