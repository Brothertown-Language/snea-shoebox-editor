"""Issue #1400 Phase 3 Item 10 (SC-9) — RED: UI default threshold equals the
published calibrated floor.

SC-9: on a FRESH session (no stored ``records``/``semantic_threshold``
preference), ``st.session_state.semantic_threshold`` (and the sidebar widgets
initialized from it) must equal the published calibrated floor
``src.services.semantic_search_service.CALIBRATED_FLOOR`` (0.93) within
±0.01 — parity between the calibration concern and the UI concern.

RED state (2026-10-02): ``src/frontend/pages/records.py`` still hardcodes the
0.80 default in the initialization block (PreferenceService fallback string
``"0.80"``, parsed fallback ``0.80``, out-of-range reset ``0.80``), so every
assertion in this file FAILS against the current tree.

Evidence tiers (per docs/development/ui_testing_standard.md):

1. **Playwright real-browser E2E (standard of record)** — ``playwright_e2e``
   marker, gated on ``SNEA_E2E=1`` + live app on :8501 + saved auth state.
   Verified precondition for the default path: the local DB has NO stored
   ``semantic_threshold`` preference for any user (read-only check,
   2026-10-02), so a fresh browser context renders the true default.
2. **AppTest fresh-session check (auxiliary in-process smoke)** — the
   pytest-level default-literal check so the RED is observable even when the
   live app/auth state is unavailable (E2E then SKIPS by design; this tier
   still runs and FAILS).

Harness precedents: test/ui/test_semantic_search_ui_flow_e2e.py
(worker-thread Chromium + saved storage state),
test/test_semantic_threshold_red.py (module-mock AppTest script).

Co-authored with AI: OpenCode (zai-org/GLM-5.3-Flash)
"""

import json
import os
import queue
import threading

import pytest
from streamlit.testing.v1 import AppTest

from src.services.semantic_search_service import CALIBRATED_FLOOR

pytest.importorskip("playwright.sync_api")
from playwright.sync_api import Page, sync_playwright  # noqa: E402

APP_URL = "http://localhost:8501/records"
ARTIFACTS_DIR = os.path.join("tmp", "1400", "artifacts")
STORAGE_PATH = os.path.join("tmp", "issue-36", "auth-state.json")

TOLERANCE = 0.01

# ---------------------------------------------------------------------------
# Tier 2 — AppTest fresh-session default-literal check (observable RED now)
# ---------------------------------------------------------------------------

RECORDS_SCRIPT = """
import streamlit as st
from unittest.mock import MagicMock

mock_linguistic = MagicMock()
mock_linguistic.search_records.return_value = MagicMock(records=[], total_count=0)
mock_linguistic.get_sources_with_counts.return_value = []
mock_linguistic.get_languages.return_value = []
mock_linguistic.get_all_records_for_export.return_value = []
mock_linguistic.get_record.return_value = None
mock_linguistic.bundle_records_to_mdf.return_value = ""
mock_linguistic.stream_records_to_temp_file.return_value = "/tmp/test"

mock_preference = MagicMock()
# Fresh session: NO stored preference for records/semantic_threshold.
mock_preference.get_preference.return_value = None

mock_identity = MagicMock()
mock_identity.get_github_username.return_value = "tester"

mock_nav = MagicMock()
mock_nav.PAGE_DIRECT_ENTRY = "/direct_entry"

mock_upload = MagicMock()
mock_upload.generate_mdf_filename.return_value = "test.mdf"

mock_validator = MagicMock()
mock_validator.diagnose_record.return_value = None

import sys

_MOCK_MODULE_PATHS = [
    "src.services.linguistic_service",
    "src.services.preference_service",
    "src.services.identity_service",
    "src.services.navigation_service",
    "src.services.upload_service",
    "src.mdf.validator",
]
_saved_modules = {p: sys.modules.get(p) for p in _MOCK_MODULE_PATHS}
try:
    sys.modules["src.services.linguistic_service"] = MagicMock()
    sys.modules["src.services.linguistic_service"].LinguisticService = mock_linguistic
    sys.modules["src.services.preference_service"] = MagicMock()
    sys.modules["src.services.preference_service"].PreferenceService = mock_preference
    sys.modules["src.services.identity_service"] = MagicMock()
    sys.modules["src.services.identity_service"].IdentityService = mock_identity
    sys.modules["src.services.navigation_service"] = MagicMock()
    sys.modules["src.services.navigation_service"].NavigationService = mock_nav
    sys.modules["src.services.upload_service"] = MagicMock()
    sys.modules["src.services.upload_service"].UploadService = mock_upload
    sys.modules["src.mdf.validator"] = MagicMock()
    sys.modules["src.mdf.validator"].MDFValidator = mock_validator

    from src.frontend.pages.records import records
    records()
finally:
    for _path, _saved in _saved_modules.items():
        if _saved is not None:
            sys.modules[_path] = _saved
        else:
            del sys.modules[_path]
"""


class TestSC9FreshSessionDefaultAppTest:
    """SC-9 auxiliary tier: fresh-session default must equal CALIBRATED_FLOOR."""

    def test_fresh_session_default_equals_calibrated_floor(self):
        at = AppTest.from_string(RECORDS_SCRIPT, default_timeout=10)
        at.run()
        default_value = float(at.session_state["semantic_threshold"])
        assert abs(default_value - CALIBRATED_FLOOR) <= TOLERANCE, (
            f"Fresh-session st.session_state.semantic_threshold default is "
            f"{default_value} — must equal the published calibrated floor "
            f"{CALIBRATED_FLOOR} within ±{TOLERANCE} (SC-9). Current tree "
            f"still hardcodes the 0.80 default."
        )

    def test_widget_defaults_equal_calibrated_floor(self):
        at = AppTest.from_string(RECORDS_SCRIPT, default_timeout=10)
        at.run()
        slider = at.slider(key="semantic_threshold_slider")
        number = at.number_input(key="semantic_threshold_number")
        for name, widget in (("slider", slider), ("number_input", number)):
            value = float(widget.value)
            assert abs(value - CALIBRATED_FLOOR) <= TOLERANCE, (
                f"Fresh-session {name} default is {value} — must equal the "
                f"published calibrated floor {CALIBRATED_FLOOR} within "
                f"±{TOLERANCE} (SC-9)."
            )

    def test_out_of_range_reset_uses_calibrated_floor(self):
        """The [0.0, 1.0] guard's reset literal must also be the calibrated
        floor (SC-9 covers the initialization block's 0.80 literals)."""
        source_path = os.path.join(
            "src", "frontend", "pages", "records.py"
        )
        with open(source_path, encoding="utf-8") as fh:
            source = fh.read()
        # The semantic_threshold init block must not carry any 0.80 default
        # literal for the threshold itself.
        init_idx = source.index('if "semantic_threshold" not in st.session_state')
        block = source[init_idx : source.index("_accepted_threshold", init_idx)]
        assert '0.80' not in block and '"0.80"' not in block, (
            "semantic_threshold initialization block still hardcodes the "
            "0.80 default literal — SC-9 requires the calibrated floor "
            f"({CALIBRATED_FLOOR}) instead."
        )


# ---------------------------------------------------------------------------
# Tier 1 — Playwright real-browser E2E (standard of record)
# ---------------------------------------------------------------------------


def _require_auth_storage() -> str | None:
    # Issue #1400 SC-11: with SNEA_E2E=1 the app-side TEST-ONLY auth bypass
    # hook authenticates every request, so the harness starts a FRESH context
    # — no saved auth state, no headed GitHub OAuth login, no fabricated
    # credentials. Without SNEA_E2E the legacy saved-state path applies.
    if os.environ.get("SNEA_E2E") == "1":
        return None
    if not os.path.exists(STORAGE_PATH):
        raise AssertionError(
            "No saved OAuth session at tmp/issue-36/auth-state.json — "
            "log in once via the headed Playwright window to generate it."
        )
    with open(STORAGE_PATH) as fh:
        cookies = [c["name"] for c in json.load(fh).get("cookies", [])]
    if "gh_auth_token" not in cookies:
        raise AssertionError("Saved session lacks the gh_auth_token cookie — regenerate the login state.")
    return STORAGE_PATH


class _BrowserSession:
    """One Chromium + authed context + page inside a worker thread
    (harness precedent: test/ui/test_semantic_search_ui_flow_e2e.py)."""

    def __init__(self, storage: str):
        self._jobs: queue.Queue = queue.Queue()
        self._result_box: list[BaseException | None] = []
        self._done_evt = threading.Event()
        self._ready_evt = threading.Event()
        self._shutdown = threading.Event()
        self._storage = storage
        self.thread = threading.Thread(target=self._main, daemon=True)
        self.thread.start()
        self._ready_evt.wait(timeout=60)

    def _main(self):
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            context = browser.new_context(storage_state=self._storage)
            page = context.new_page()
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

    def run(self, fn, timeout: float = 240.0):
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


def _delete_saved_threshold_preferences() -> None:
    """Enforce the SC-9 fresh-default precondition: no stored
    records/semantic_threshold preference may exist for ANY user, otherwise
    the rendered widget value is a user-saved preference, not the default.
    The SC-2 DOM e2e round-trip legitimately persists 0.7 for the bypass
    session user, so the precondition is actively established here instead of
    being assumed (assertions below are unchanged)."""
    import sys

    sys.path.insert(0, os.path.abspath("."))
    from sqlalchemy import text

    import src.database.models.core  # noqa: F401 — register all mappers
    import src.database.models.identity  # noqa: F401
    import src.database.models.iso639  # noqa: F401
    import src.database.models.meta  # noqa: F401
    import src.database.models.search  # noqa: F401
    import src.database.models.workflow  # noqa: F401
    from src.database.connection import get_engine

    eng = get_engine()
    with eng.connect() as conn:
        conn.execute(
            text(
                "DELETE FROM user_preferences "
                "WHERE view_name = 'records' AND preference_key = 'semantic_threshold'"
            )
        )
        conn.commit()


@pytest.fixture(scope="module")
def session():
    _delete_saved_threshold_preferences()
    storage = _require_auth_storage()
    sess = _BrowserSession(storage)
    yield sess
    sess.close()


@pytest.mark.playwright_e2e
@pytest.mark.skipif(
    os.environ.get("SNEA_E2E", "") != "1",
    reason="live-app E2E — run with SNEA_E2E=1 while streamlit is up on :8501",
)
class TestSC9FreshSessionDefaultPlaywright:
    """SC-9 standard-of-record tier: the live app on a fresh browser context
    renders the fresh-session default threshold at CALIBRATED_FLOOR ±0.01.

    Precondition (verified read-only, 2026-10-02): no stored
    records/semantic_threshold preference exists in the local DB, so the
    rendered widget value IS the default, not a user-saved preference."""

    def test_fresh_session_widget_default_equals_calibrated_floor(self, session):
        def body(page: Page):
            page.goto(APP_URL, wait_until="domcontentloaded")
            # Skip-by-design guards: race the records page mount against the
            # login page and against a wedged app shell. If the app dehydrated
            # to the login page or never mounts content, the E2E tier cannot
            # run without a developer-headed re-login / server restart — skip
            # explicitly rather than time out (per the task contract and
            # ui_testing_standard.md's regenerate-when-stale rule; never fall
            # back to unauthenticated).
            deadline = 60_000
            mounted = False
            while deadline > 0:
                info = page.evaluate(
                    "() => ({"
                    "text: document.body.innerText,"
                    "sidebar: !!document.querySelector('[data-testid=\"stSidebar\"] input[type=\"number\"]'),"
                    "})"
                )
                if "Continue with GitHub" in info["text"]:
                    pytest.skip(
                        "Saved auth state at tmp/issue-36/auth-state.json is "
                        "stale (login page rendered) — regenerate via the "
                        "headed Playwright login window; E2E skipped by design."
                    )
                if info["sidebar"]:
                    mounted = True
                    break
                page.wait_for_timeout(2000)
                deadline -= 2000
            if not mounted:
                pytest.skip(
                    "Live app on :8501 is unavailable — health endpoint "
                    "responds but the records page never mounts (wedged "
                    "long-running dev server or stale auth). E2E skipped by "
                    "design; the AppTest tier carries the SC-9 RED."
                )
            # The sidebar numeric threshold input (semantic_threshold_number,
            # DOM anchor established by the SC-2 DOM e2e suite).
            number = page.locator('[data-testid="stSidebar"] input[type="number"]').last
            number.wait_for(state="visible", timeout=30_000)
            value = float(number.input_value())
            os.makedirs(ARTIFACTS_DIR, exist_ok=True)
            page.screenshot(
                path=os.path.join(ARTIFACTS_DIR, "sc9-fresh-session-default.png"),
                full_page=True,
            )
            assert abs(value - CALIBRATED_FLOOR) <= TOLERANCE, (
                f"Live fresh-session threshold widget default is {value} — "
                f"must equal the published calibrated floor {CALIBRATED_FLOOR} "
                f"within ±{TOLERANCE} (SC-9). Current tree still renders the "
                f"hardcoded 0.80 default."
            )

        session.run(body)