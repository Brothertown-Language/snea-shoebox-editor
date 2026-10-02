"""SC-1 (#1392): Access Restricted dialog renders the resolved maintainer
contact label — never the raw ``<MAINTAINER_CONTACT>`` token.

Evidence type: behavioral (Playwright real-browser test against the live app
on :8501, per docs/development/ui_testing_standard.md and test/ui/AGENTS.md).

Auth model: the app process is restarted with SNEA_SIMULATE_AUTH=unauthorized
(the legacy local-mode hook, which takes precedence over the SNEA_E2E bypass
in src/services/security_manager.py::rehydrate_session); the saved OAuth
storage state at tmp/issue-1385/auth-state.json (carrying the app's own
gh_auth_token cookie; sanity-checked before use — never fabricated)
supplies the authenticated transport. The unauthorized (Access Restricted)
dialog is shown when
IdentityService marks the session unauthorized; the dialog body must contain
``contact.maintainer_label`` ("Michael Conrad (@michaelconrad on Mastodon)")
and must NOT contain the literal ``<MAINTAINER_CONTACT>`` token.

RED provenance: the pre-fix tree (bdac900~1) rendered the literal f-string
``"...<MAINTAINER_CONTACT>: [{mastodon_url}]({mastodon_url})"`` to end users —
that is the filed bug. tmp/issue-1392/red-sc1-prefix-demo.py executes this
module's assertion helper against that pre-fix rendering and exits non-zero,
which is the executed RED event; see that artifact's log for the run.

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
        reason="live-app E2E — run with SNEA_E2E=1 while streamlit is up on :8501",
    ),
]


def _require_auth_storage() -> str:
    if not os.path.exists(STORAGE_PATH):
        raise AssertionError(
            "No saved OAuth session at tmp/issue-1385/auth-state.json — "
            "log in once via the headed Playwright window to generate it."
        )
    with open(STORAGE_PATH) as fh:
        cookies = [c["name"] for c in json.load(fh).get("cookies", [])]
    if "gh_auth_token" not in cookies:
        raise AssertionError("Saved session lacks the gh_auth_token cookie — regenerate the login state.")
    return STORAGE_PATH


def assert_dialog_text_has_no_raw_token(dialog_text: str) -> None:
    """SC-1 assertions on the Access Restricted dialog text.

    Shared by the live Playwright test and the RED pre-fix demonstration:
    the dialog must show the resolved maintainer label and never the raw
    ``<MAINTAINER_CONTACT>`` token.
    """
    assert dialog_text, "Access Restricted dialog text was empty — dialog did not render."
    assert RAW_TOKEN not in dialog_text, (
        f"Access Restricted dialog shows the raw {RAW_TOKEN!r} token to end users "
        f"instead of the resolved contact.maintainer_label value. Dialog text: {dialog_text!r}"
    )
    assert MAINTAINER_LABEL in dialog_text, (
        f"Access Restricted dialog does not show contact.maintainer_label "
        f"({MAINTAINER_LABEL!r}). Dialog text: {dialog_text!r}"
    )


def _health_ok() -> bool:
    try:
        with urllib.request.urlopen(HEALTH_URL, timeout=2) as resp:
            return resp.status == 200
    except (urllib.error.URLError, OSError):
        return False


def _restart_app(sim_value: str | None) -> None:
    """Restart the local Streamlit app, optionally carrying SNEA_SIMULATE_AUTH.

    The SNEA_SIMULATE_AUTH hook resolves BEFORE the SNEA_E2E bypass in
    SecurityManager.rehydrate_session, so a fresh app process started with
    SNEA_SIMULATE_AUTH=unauthorized yields the legacy unauthorized state
    (Access Restricted dialog) while the default (sim unset) keeps the
    SNEA_E2E bypass-authenticated session.
    """
    subprocess.run(["pkill", "-f", "streamlit run streamlit_app.py"], check=False, capture_output=True)
    deadline = time.monotonic() + 20
    while time.monotonic() < deadline and _health_ok():
        time.sleep(0.5)

    env = dict(os.environ)
    env.pop(SIM_ENV_VAR, None)
    if sim_value is not None:
        env[SIM_ENV_VAR] = sim_value

    log_path = os.path.join(ARTIFACTS_DIR, f"streamlit-sc1-{sim_value or 'clean'}.log")
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)
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
def _restore_bypass_app():
    """Leave the app running with the SNEA_E2E bypass (sim variable unset)."""
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


def test_access_restricted_dialog_shows_resolved_maintainer_label_sc1():
    """SC-1: the Access Restricted dialog renders contact.maintainer_label,
    never the raw <MAINTAINER_CONTACT> token."""
    storage = _require_auth_storage()
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)
    screenshot = os.path.join(ARTIFACTS_DIR, "e2e-sc1-login-dialog.png")
    _restart_app("unauthorized")

    def _body():
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            context = browser.new_context(storage_state=storage)
            page = context.new_page()
            page.goto(APP_URL, wait_until="domcontentloaded")
            # Streamlit renders progressively; wait for the dialog to surface.
            dialog = page.get_by_text("Access Restricted").first
            dialog.wait_for(state="visible", timeout=30_000)
            # Give the dialog body one websocket frame to finish rendering.
            page.wait_for_timeout(1500)
            body_text = page.locator("[data-testid='stDialog'] *, [role='dialog'] *").all_inner_texts()
            dialog_text = "\n".join(t or "" for t in body_text) if body_text else page.inner_text("body")
            page.screenshot(path=screenshot, full_page=True)
            browser.close()

        assert_dialog_text_has_no_raw_token(dialog_text)

    _run_in_worker_thread(_body)
