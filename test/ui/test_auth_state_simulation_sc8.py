"""SC-8 (#1392): SNEA_SIMULATE_AUTH drives the live app's three auth states.

Evidence type: behavioral (Playwright real-browser tests against the live app
on :8501, per docs/development/ui_testing_standard.md and test/ui/AGENTS.md).

The hook is honored by the app's identity path ONLY when the secrets
``[runtime]`` mode equals "local" (production inertness is verified at unit
level by test/test_auth_simulation_sc8.py::test_sc8_hook_gated_on_local_mode).

This module owns the app lifecycle: each state test restarts the local app
process with the corresponding ``SNEA_SIMULATE_AUTH`` value (the app picks up
the env var at process start), waits for ``/_stcore/health`` → 200, then
drives a real Chromium against it. The saved OAuth storage state
(tmp/issue-1385/auth-state.json, carrying the app's own ``gh_auth_token``
cookie) supplies the authenticated transport for all three states — no
browser auth cookies are fabricated. The module restores the app WITHOUT the
simulation variable when it finishes.

States asserted (spec SC-8 parameter domain):
- ``unauthorized`` → Access Restricted dialog renders with the resolved
  ``contact.maintainer_label`` text, never the raw ``<MAINTAINER_CONTACT>``
  token (also SC-1's dialog assertion).
- ``authorized``   → identity syncs; the app proceeds past login to the main
  app (no dialog, no /login redirect, main-menu content renders).
- ``anonymous``    → redirects to /login without the dialog.

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

import json
import os
import subprocess
import threading
import time
import urllib.error
import urllib.request

import pytest
from playwright.sync_api import sync_playwright

APP_URL = "http://localhost:8501"
HEALTH_URL = f"{APP_URL}/_stcore/health"
ARTIFACTS_DIR = os.path.join("tmp", "issue-1392", "artifacts")
STORAGE_PATH = os.path.join("tmp", "issue-1385", "auth-state.json")
MAINTAINER_LABEL = "Michael Conrad (@michaelconrad on Mastodon)"
RAW_TOKEN = "<MAINTAINER_CONTACT>"
SIM_ENV_VAR = "SNEA_SIMULATE_AUTH"

pytest.importorskip("playwright.sync_api")

pytestmark = [
    pytest.mark.playwright_e2e,
    pytest.mark.skipif(
        os.environ.get("SNEA_E2E", "") != "1",
        reason="live-app E2E — run with SNEA_E2E=1 (this module manages the app process)",
    ),
]


def _require_auth_storage() -> str:
    if not os.path.exists(STORAGE_PATH):
        raise AssertionError(
            "No saved OAuth session at tmp/issue-1385/auth-state.json — "
            "regenerate it via the headed-login procedure (never fabricate)."
        )
    with open(STORAGE_PATH) as fh:
        cookies = [c["name"] for c in json.load(fh).get("cookies", [])]
    if "gh_auth_token" not in cookies:
        raise AssertionError("Saved session lacks the gh_auth_token cookie — regenerate the login state.")
    return STORAGE_PATH


def _health_ok() -> bool:
    try:
        with urllib.request.urlopen(HEALTH_URL, timeout=2) as resp:
            return resp.status == 200
    except (urllib.error.URLError, OSError):
        return False


def _restart_app(sim_value: str | None) -> None:
    """Restart the local Streamlit app, optionally carrying SNEA_SIMULATE_AUTH.

    The simulation hook is read from the app process's environment, so each
    state requires a fresh process started with that value (or without it).
    """
    subprocess.run(
        ["pkill", "-f", "streamlit run streamlit_app.py"],
        check=False,
        capture_output=True,
    )
    # Wait for the old process to actually release :8501.
    deadline = time.monotonic() + 20
    while time.monotonic() < deadline and _health_ok():
        time.sleep(0.5)

    env = dict(os.environ)
    env.pop(SIM_ENV_VAR, None)
    if sim_value is not None:
        env[SIM_ENV_VAR] = sim_value

    log_path = os.path.join(
        "tmp", "issue-1392", f"streamlit-sc8-{sim_value or 'clean'}.log"
    )
    os.makedirs("tmp/issue-1392", exist_ok=True)
    with open(log_path, "w") as log_fh:
        subprocess.Popen(
            [
                "uv", "run", "--extra", "local", "python", "-m", "streamlit",
                "run", "streamlit_app.py",
                "--server.address", "0.0.0.0", "--server.port", "8501",
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
def _restore_clean_app():
    """Leave the app running WITHOUT the simulation variable after the module."""
    yield
    try:
        _restart_app(None)
    except Exception:  # noqa: BLE001 — teardown must not mask test results
        pass


def _run_in_worker_thread(fn):
    """Run a sync_playwright body in a worker thread (pytest 9 + anyio keeps
    an asyncio loop on the main thread; the Playwright sync API forbids
    entering under a running loop)."""
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


def test_sc8_unauthorized_renders_access_restricted_dialog():
    """unauthorized → is_unauthorized → Access Restricted dialog with the
    resolved maintainer label and no raw <MAINTAINER_CONTACT> token."""
    storage = _require_auth_storage()
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)
    screenshot = os.path.join(ARTIFACTS_DIR, "e2e-sc8-unauthorized-dialog.png")
    _restart_app("unauthorized")

    def _body():
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            context = browser.new_context(storage_state=storage)
            page = context.new_page()
            page.goto(APP_URL, wait_until="domcontentloaded")
            dialog = page.get_by_text("Access Restricted").first
            dialog.wait_for(state="visible", timeout=30_000)
            page.wait_for_timeout(1500)
            body_text = page.locator("[data-testid='stDialog'] *, [role='dialog'] *").all_inner_texts()
            dialog_text = "\n".join(t or "" for t in body_text) if body_text else page.inner_text("body")
            page.screenshot(path=screenshot, full_page=True)
            browser.close()

        assert dialog_text, "Access Restricted dialog did not render."
        assert RAW_TOKEN not in dialog_text, (
            f"Dialog shows the raw {RAW_TOKEN!r} token. Dialog text: {dialog_text!r}"
        )
        assert MAINTAINER_LABEL in dialog_text, (
            f"Dialog does not show contact.maintainer_label ({MAINTAINER_LABEL!r}). "
            f"Dialog text: {dialog_text!r}"
        )

    _run_in_worker_thread(_body)


def test_sc8_authorized_syncs_identity_to_main_app():
    """authorized → identity syncs; app proceeds past login to the main app."""
    storage = _require_auth_storage()
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)
    screenshot = os.path.join(ARTIFACTS_DIR, "e2e-sc8-authorized-main-app.png")
    _restart_app("authorized")

    def _body():
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            context = browser.new_context(storage_state=storage)
            page = context.new_page()
            page.goto(APP_URL, wait_until="domcontentloaded")
            # Identity sync runs on first load; the main menu then renders.
            main_menu = page.get_by_text("Database Statistics").first
            main_menu.wait_for(state="visible", timeout=45_000)
            page.wait_for_timeout(1500)
            page_text = page.inner_text("body")
            page.screenshot(path=screenshot, full_page=True)
            final_url = page.url
            browser.close()

        assert "Access Restricted" not in page_text, (
            f"authorized state must NOT render the Access Restricted dialog. Body: {page_text[:500]!r}"
        )
        assert "/login" not in final_url, (
            f"authorized state must NOT redirect to /login (final URL: {final_url})"
        )

    _run_in_worker_thread(_body)


def test_sc8_anonymous_redirects_to_login_without_dialog():
    """anonymous → unauthenticated outcome; app redirects to /login, no dialog."""
    storage = _require_auth_storage()
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)
    screenshot = os.path.join(ARTIFACTS_DIR, "e2e-sc8-anonymous-login.png")
    _restart_app("anonymous")

    def _body():
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            context = browser.new_context(storage_state=storage)
            page = context.new_page()
            page.goto(APP_URL, wait_until="domcontentloaded")
            # The app clears auth state and reruns → redirect to the login page.
            page.wait_for_url("**/login", timeout=45_000)
            page.wait_for_timeout(1500)
            page_text = page.inner_text("body")
            page.screenshot(path=screenshot, full_page=True)
            final_url = page.url
            browser.close()

        assert "Access Restricted" not in page_text, (
            f"anonymous state must NOT render the Access Restricted dialog. Body: {page_text[:500]!r}"
        )
        assert "/login" in final_url, f"anonymous state must land on /login (final URL: {final_url})"

    _run_in_worker_thread(_body)
