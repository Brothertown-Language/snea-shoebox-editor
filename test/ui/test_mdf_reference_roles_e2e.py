"""SC-10: the MDF Reference page is reachable and readable by every
authenticated role (viewer, editor, admin), via the R-15 TEST-ONLY role
selection (SNEA_E2E_ROLE, honored exclusively under SNEA_E2E=1).

Each test restarts the local app with the role variable set, then drives a
fresh browser context through the app-side SNEA_E2E auth bypass. Role
evidence comes from the production RBAC path itself: get_user_role walks the
synced DB's Permission rows, and the bypass swaps in the role's seed team so
each session resolves its role through that real walk. The page itself gates
nothing by role (it is a reference browser for every authenticated user), so
the per-role assertions are the user-visible single-rail contract: the page
renders and is readable, the global sidebar nav stays hidden, and the
standard back-to-main affordance is present. The module fixture restores the
default bypass app (no role override) afterwards.

Harness conventions follow test_playwright_backfill_clickthrough.py.

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

import os
import subprocess
import threading
import time
import urllib.error
import urllib.request

import pytest
from playwright.sync_api import sync_playwright

# App port parameterized (SNEA_E2E_PORT) so the harness can run against a
# dedicated app instance without touching a developer-owned app on :8501.
E2E_PORT = os.environ.get("SNEA_E2E_PORT", "8501")
APP_URL = f"http://localhost:{E2E_PORT}"
MDF_URL = f"{APP_URL}/mdf-reference"
ARTIFACTS_DIR = os.path.join("tmp", "issue-1379", "artifacts")
HEALTH_URL = f"{APP_URL}/_stcore/health"
ROLE_ENV_VAR = "SNEA_E2E_ROLE"
HOME_HEADING = "Helps Database for MDF Marker Set"

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


def _restart_app(role: str | None) -> None:
    """Restart the app under test with SNEA_E2E_ROLE set (or cleared).

    The pattern targets only this harness's configured port, so apps on
    other ports (e.g. a developer-owned instance on :8501) are untouched.
    """
    subprocess.run(["pkill", "-f", f"server.port {E2E_PORT}"], check=False, capture_output=True)
    deadline = time.monotonic() + 20
    while time.monotonic() < deadline and _health_ok():
        time.sleep(0.5)

    env = dict(os.environ)
    env["SNEA_E2E"] = "1"
    env.pop("SNEA_SIMULATE_AUTH", None)
    env.pop(ROLE_ENV_VAR, None)
    if role is not None:
        env[ROLE_ENV_VAR] = role

    log_path = os.path.join(ARTIFACTS_DIR, f"streamlit-role-{role or 'default'}.log")
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)
    with open(log_path, "w") as log_fh:
        subprocess.Popen(
            [
                "uv", "run", "--extra", "local", "python", "-m", "streamlit",
                "run", "streamlit_app.py",
                "--server.address", "0.0.0.0", "--server.port", E2E_PORT,
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
    raise AssertionError(f"App did not become healthy on :8501 (SNEA_E2E_ROLE={role!r}).")


@pytest.fixture(scope="module", autouse=True)
def _restore_default_bypass_app():
    """Leave the app running with the default SNEA_E2E bypass (role unset)."""
    yield
    try:
        _restart_app(None)
    except Exception:  # noqa: BLE001 — teardown must not mask test results
        pass


def _role_flow(role: str, screenshot_name: str) -> dict:
    """Restart the app for `role`, open the MDF Reference page in a fresh
    context, and return the single-rail page state for assertions."""

    def flow():
        _restart_app(role)
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            try:
                page = browser.new_context(storage_state=None).new_page()
                page.goto(MDF_URL)
                page.wait_for_selector(f"h2:has-text('{HOME_HEADING}')", timeout=90_000)
                page.wait_for_timeout(1500)
                nav = page.locator('[data-testid="stSidebarNav"]')
                nav_visible = nav.count() > 0 and nav.first.is_visible()
                back_button = page.get_by_role("button", name="Back to Main Menu").count() > 0
                body = page.inner_text("body")
                page.screenshot(path=os.path.join(ARTIFACTS_DIR, screenshot_name))
                return {"nav_visible": nav_visible, "back_button": back_button, "body": body}
            finally:
                browser.close()

    box: list[BaseException | None] = []
    result: list = []

    def _target():
        try:
            result.append(flow())
            box.append(None)
        except BaseException as e:  # noqa: BLE001 — propagate verbatim
            box.append(e)

    t = threading.Thread(target=_target)
    t.start()
    t.join()
    err = box[0]
    if err is not None:
        raise err
    return result[0]


def test_sc10_viewer_reaches_mdf_reference():
    state = _role_flow("viewer", "sc10-01-viewer.png")
    assert not state["nav_visible"], (
        "the global sidebar nav must stay hidden — the MDF browser is the single left rail"
    )
    assert state["back_button"], "viewer must have the standard back-to-main affordance"
    assert HOME_HEADING in state["body"], "viewer must be able to read the page content"


def test_sc10_editor_reaches_mdf_reference():
    state = _role_flow("editor", "sc10-02-editor.png")
    assert not state["nav_visible"], (
        "the global sidebar nav must stay hidden — the MDF browser is the single left rail"
    )
    assert state["back_button"], "editor must have the standard back-to-main affordance"
    assert HOME_HEADING in state["body"], "editor must be able to read the page content"


def test_sc10_admin_reaches_mdf_reference():
    state = _role_flow("admin", "sc10-03-admin.png")
    assert not state["nav_visible"], (
        "the global sidebar nav must stay hidden — the MDF browser is the single left rail"
    )
    assert state["back_button"], "admin must have the standard back-to-main affordance"
    assert HOME_HEADING in state["body"], "admin must be able to read the page content"
