"""SC-3: Playwright real-browser verification for the v8 design — the
"∞→ꝏ Remediation" section lives INSIDE the Data Reprocessing view and the
Table Maintenance sidebar has NO fourth radio option (issue #1382, spec v8,
plan step 38).

Auth model: with SNEA_E2E=1 the app-side TEST-ONLY auth bypass hook
(src/services/security_manager.py) authenticates a FRESH browser context —
no saved storage state, no headed GitHub OAuth login, no fabricated
credentials (Issue #1400 SC-11). The non-admin (anonymous) flow restarts the
app with SNEA_SIMULATE_AUTH=anonymous, which takes precedence over the
bypass, so the deep-link redirect to /login proves the admin guard denied
access — same evidence pattern as test_playwright_backfill_clickthrough.py.

Co-authored with AI: OpenCode (zai-org/GLM-5.3-Flash)
"""

import os
import subprocess
import threading
import time
import urllib.error
import urllib.request

import pytest
from playwright.sync_api import sync_playwright

APP_URL = "http://localhost:8501"
MAINTENANCE_URL = "http://localhost:8501/maintenance"
ARTIFACTS_DIR = os.path.join("tmp", "issue-1382", "artifacts")
SIM_ENV_VAR = "SNEA_SIMULATE_AUTH"
HEALTH_URL = f"{APP_URL}/_stcore/health"

SECTION_TITLE = "∞→ꝏ Remediation"
EXISTING_OPTIONS = ["Sources", "Soft Deleted Records", "Data Reprocessing"]

pytest.importorskip("playwright.sync_api")

pytestmark = [
    pytest.mark.playwright_e2e,
    pytest.mark.skipif(
        os.environ.get("SNEA_E2E", "") != "1",
        reason="live-app E2E — run with SNEA_E2E=1 while streamlit is up on :8501",
    ),
]


def _health_ok() -> bool:
    try:
        with urllib.request.urlopen(HEALTH_URL, timeout=2) as resp:
            return resp.status == 200
    except (urllib.error.URLError, OSError):
        return False


def _restart_app(sim_value: str | None) -> None:
    """Restart the local Streamlit app, optionally carrying SNEA_SIMULATE_AUTH."""
    subprocess.run(["pkill", "-f", "streamlit run streamlit_app.py"], check=False, capture_output=True)
    deadline = time.monotonic() + 20
    while time.monotonic() < deadline and _health_ok():
        time.sleep(0.5)

    env = dict(os.environ)
    env.pop(SIM_ENV_VAR, None)
    if sim_value is not None:
        env[SIM_ENV_VAR] = sim_value

    log_path = os.path.join(ARTIFACTS_DIR, f"streamlit-sc3-{sim_value or 'clean'}.log")
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)
    with open(log_path, "w") as log_fh:
        subprocess.Popen(
            [
                "uv", "run", "--extra", "local", "python", "-m", "streamlit",
                "run", "streamlit_app.py",
                "--server.address", "0.0.0.0", "--server.port", "8501",
                "--server.headless", "true",
            ],
            env=env,
            stdout=log_fh,
            stderr=subprocess.STDOUT,
        )

    deadline = time.monotonic() + 90
    while time.monotonic() < deadline:
        if _health_ok():
            return
        time.sleep(1.0)
    raise AssertionError(f"App did not become healthy on :8501 (SNEA_SIMULATE_AUTH={sim_value!r}).")


@pytest.fixture(scope="module", autouse=True)
def _restore_bypass_app():
    """Leave the app running with the SNEA_E2E bypass (sim variable unset)."""
    yield
    try:
        _restart_app(None)
    except Exception:  # noqa: BLE001 — teardown must not mask test results
        pass


def _run_in_worker_thread(fn):
    """Run a sync_playwright body in a worker thread (pytest 9 + anyio)."""
    box: list[BaseException | None] = []

    def _target():
        try:
            fn()
            box.append(None)
        except BaseException as e:  # noqa: BLE001 — propagate test failure verbatim
            box.append(e)

    t = threading.Thread(target=_target)
    t.start()
    t.join()
    err = box[0]
    if err is not None:
        raise err


def _admin_flow():
    """Admin: open /maintenance via the SNEA_E2E bypass, verify the sidebar
    radio has NO fourth "∞→ꝏ Remediation" option, then select "Data
    Reprocessing" and verify the ∞→ꝏ Remediation section renders inside that
    view."""
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        try:
            page = browser.new_page()
            page.goto(MAINTENANCE_URL)
            page.wait_for_selector("text=Maintenance Tables", timeout=60_000)
            page.screenshot(path=os.path.join(ARTIFACTS_DIR, "sc3-admin-sidebar-loaded.png"))

            # The sidebar radio must NOT contain the fourth option.
            body = page.inner_text("body")
            assert SECTION_TITLE not in body, (
                f'"∞→ꝏ Remediation" must NOT be a sidebar option in the v8 '
                f"design; body tail: {body[-800:]}"
            )
            for option in EXISTING_OPTIONS:
                assert option in body, f"Existing option {option!r} missing from sidebar"
            page.screenshot(path=os.path.join(ARTIFACTS_DIR, "sc3-admin-three-options.png"))

            # Click "Data Reprocessing" and verify the ∞→ꝏ Remediation
            # section renders inside this view (section title visible).
            page.get_by_text("Data Reprocessing", exact=True).click()
            page.wait_for_timeout(3000)
            body2 = page.inner_text("body")
            page.screenshot(path=os.path.join(ARTIFACTS_DIR, "sc3-admin-data-reprocessing-view.png"))
            assert SECTION_TITLE in body2, (
                f'"∞→ꝏ Remediation" section absent from the Data Reprocessing '
                f"view; body tail: {body2[-800:]}"
            )
            assert "permission" not in body2.lower() or "admin role required" not in body2.lower(), (
                f"Admin was blocked by the permission guard; body: {body2[-800:]}"
            )
        finally:
            browser.close()


def test_admin_data_reprocessing_view_shows_remediation_section_without_fourth_option():
    """Admin session: sidebar has exactly the three original options (no
    fourth "∞→ꝏ Remediation" radio option) and the Data Reprocessing view
    renders the ∞→ꝏ Remediation section."""
    _restart_app(None)
    _run_in_worker_thread(_admin_flow)


def _non_admin_flow():
    """Unauthenticated browser: /maintenance deep-link redirects to /login —
    the admin guard denies access (SNEA_SIMULATE_AUTH=anonymous takes
    precedence over the SNEA_E2E bypass)."""
    _restart_app("anonymous")
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        try:
            page = browser.new_page()
            page.goto(MAINTENANCE_URL)
            page.wait_for_url("**/login", timeout=30_000)
            page.screenshot(path=os.path.join(ARTIFACTS_DIR, "sc3-nonadmin-redirect-login.png"))
            body = page.inner_text("body")
            assert SECTION_TITLE not in body, "Remediation section visible without admin role"
            for option in EXISTING_OPTIONS:
                assert option not in body, f"Option {option!r} visible without admin role"
            assert "Login" in page.title() or page.url.rstrip("/").endswith("/login"), (
                f"Expected login page redirect; got URL={page.url!r}"
            )
        finally:
            browser.close()


def test_non_admin_blocked_by_admin_guard():
    """Unauthenticated browser reaches the login flow, never the maintenance
    sidebar options."""
    _run_in_worker_thread(_non_admin_flow)