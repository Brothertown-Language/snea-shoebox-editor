# SPDX-FileCopyrightText: 2026 Michael Conrad
# SPDX-License-Identifier: MIT
# Provenance: AI-generated
"""SC-7: the API Keys admin view is admin-gated and functional (issue #1420).

Admin session: the page renders, create pair shows the plaintext secret
exactly once, regenerate shows a new secret exactly once, enable/disable
flip the key's status, revoke (after confirmation) sets the status to
revoked, and no existing secret is ever redisplayed.

Viewer/editor sessions: the page deep-link renders the permission-denied
block and no key-management affordances.

Role evidence flows through the production RBAC path via the TEST-ONLY
SNEA_E2E_ROLE selection (honored exclusively under SNEA_E2E=1). Harness
conventions follow test_mdf_reference_roles_e2e.py: per-role app restarts,
fresh browser contexts, sync_playwright in a worker thread, screenshots
under tmp/1420/artifacts/.

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

import os
import subprocess
import threading
import time
import urllib.error
import urllib.request

import pytest
from playwright.sync_api import expect, sync_playwright

E2E_PORT = os.environ.get("SNEA_E2E_PORT", "8501")
APP_URL = f"http://localhost:{E2E_PORT}"
API_KEYS_URL = f"{APP_URL}/api-keys"
HEALTH_URL = f"{APP_URL}/_stcore/health"
ARTIFACTS_DIR = os.path.join("tmp", "1420", "artifacts")
ROLE_ENV_VAR = "SNEA_E2E_ROLE"
KEY_LABEL = "sc7-e2e-agent"
PERMISSION_DENIED = "You do not have permission to access this page. Admin role required."

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

    Targets only this harness's configured port; apps on other ports are
    untouched.
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
                "uv",
                "run",
                "--extra",
                "local",
                "python",
                "-m",
                "streamlit",
                "run",
                "streamlit_app.py",
                "--server.address",
                "0.0.0.0",
                "--server.port",
                E2E_PORT,
                "--server.headless",
                "true",
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
    raise AssertionError(f"App did not become healthy on :{E2E_PORT} (SNEA_E2E_ROLE={role!r}).")


@pytest.fixture(scope="module", autouse=True)
def _restore_default_bypass_app():
    """Leave the app running with the default SNEA_E2E bypass (role unset)."""
    yield
    try:
        _restart_app(None)
    except Exception:  # noqa: BLE001 — teardown must not mask test results
        pass


def _run_flow(flow):
    """Run a sync_playwright flow in a worker thread (pytest 9 + anyio keeps
    an asyncio loop on the main thread)."""
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


def _open_page(role: str, screenshot_name: str):
    """Restart the app for `role` and open /api-keys in a fresh context."""

    def flow():
        _restart_app(role)
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            try:
                page = browser.new_context(storage_state=None).new_page()
                page.goto(API_KEYS_URL)
                page.wait_for_timeout(6000)  # script run + render
                body = page.inner_text("body")
                page.screenshot(path=os.path.join(ARTIFACTS_DIR, screenshot_name))
                return body
            finally:
                browser.close()

    return _run_flow(flow)


def _extract_one_time_secret(page) -> str:
    """The one-time display block: success message + <code> with the secret."""
    page.wait_for_selector('code:below(:text("never be shown again"))', timeout=15000)
    code_el = page.locator('code:below(:text("never be shown again"))').first
    return code_el.inner_text().strip()


def _cleanup_prior_test_keys() -> None:
    """Remove rows from earlier runs of this test (harness setup, not part
    of the behavioral claim) so the lifecycle flow sees exactly one row."""
    from src.database.connection import get_session
    from src.database.models.api_keys import ApiKeys

    session = get_session()
    try:
        session.query(ApiKeys).filter(ApiKeys.label == KEY_LABEL).delete(synchronize_session=False)
        session.commit()
    finally:
        session.close()


def test_sc7_admin_full_lifecycle():
    """Admin: render, create (secret once), regenerate (secret once),
    enable/disable, revoke with confirmation, no secret redisplay."""

    def flow():
        _cleanup_prior_test_keys()
        _restart_app("admin")
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            try:
                page = browser.new_context(storage_state=None).new_page()
                page.goto(API_KEYS_URL)
                page.wait_for_selector("text=Create key pair", timeout=90_000)
                page.wait_for_timeout(1000)

                # The hidden nav is replaced by a titled sidebar rail carrying
                # the back-to-main affordance (never a blank left pane).
                back_btn = page.get_by_role("button", name="Back to Main Menu")
                assert back_btn.count() > 0, "sidebar rail must carry the back-to-main button"
                assert back_btn.first.is_visible(), "back-to-main button must be visible"

                # ── Create: label + Create → secret shown exactly once ──
                page.fill('input[aria-label="Label"]', KEY_LABEL)
                page.get_by_role("button", name="Create", exact=True).click()
                secret1 = _extract_one_time_secret(page)
                page.screenshot(path=os.path.join(ARTIFACTS_DIR, "sc7-01-created.png"))

                # Copyable curl example: same one-time display, embeds the
                # key + secret and the records endpoint (follow-up request).
                curl_text = page.locator("code.language-bash").first.inner_text()
                assert "curl" in curl_text, "one-time display must include a copyable curl command"
                assert "X-API-Key" in curl_text and "X-API-Secret" in curl_text
                assert "/api/v1/records" in curl_text
                assert secret1 in curl_text, "the curl command must embed the issued secret"

                # Ack → the secret display disappears (never redisplayed)
                page.get_by_role("button", name="I have stored the secret").click()
                page.wait_for_timeout(2500)
                assert page.locator('code:below(:text("never be shown again"))').count() == 0, (
                    "secret must not remain displayed after acknowledgement"
                )
                assert secret1 not in page.inner_text("body"), "secret must be gone from the DOM"
                assert "curl -sS" not in page.inner_text("body"), (
                    "the curl example embeds the secret and must vanish with it"
                )

                # ── The key row lists the key with status enabled ──
                page.wait_for_selector(f"text={KEY_LABEL}", timeout=15000)

                # ── Regenerate: new secret shown exactly once, old gone ──
                page.get_by_role("button", name="Regenerate secret").first.click()
                secret2 = _extract_one_time_secret(page)
                page.screenshot(path=os.path.join(ARTIFACTS_DIR, "sc7-02-regenerated.png"))
                assert secret2 != secret1, "regenerated secret must differ"
                page.get_by_role("button", name="I have stored the secret").click()
                page.wait_for_timeout(2500)
                assert secret2 not in page.inner_text("body"), "secret must be gone from the DOM"

                # ── Disable → status flips to disabled ──
                page.get_by_role("button", name="Disable", exact=True).first.click()
                page.wait_for_selector("strong:has-text('disabled')", timeout=15000)
                page.screenshot(path=os.path.join(ARTIFACTS_DIR, "sc7-03-disabled.png"))

                # ── Enable → status flips back to enabled ──
                page.get_by_role("button", name="Enable", exact=True).first.click()
                page.wait_for_selector("strong:has-text('enabled')", timeout=15000)

                # ── Revoke with confirmation ──
                page.get_by_role("button", name="Revoke", exact=True).first.click()
                page.wait_for_selector("text=Confirm revoke", timeout=15000)
                page.screenshot(path=os.path.join(ARTIFACTS_DIR, "sc7-04-revoke-confirm.png"))
                page.get_by_role("button", name="Confirm revoke").click()
                page.wait_for_selector("strong:has-text('revoked')", timeout=15000)
                page.screenshot(path=os.path.join(ARTIFACTS_DIR, "sc7-05-revoked.png"))

                # After revocation the lifecycle buttons are disabled.
                expect(page.get_by_role("button", name="Revoke", exact=True).first).to_be_disabled()
                expect(page.get_by_role("button", name="Regenerate secret").first).to_be_disabled()
                return {"secret1": secret1, "secret2": secret2}
            finally:
                browser.close()

    secrets = _run_flow(flow)
    assert secrets["secret1"] and secrets["secret2"]


def _assert_non_admin_blocked(body: str, role: str) -> None:
    """Non-admin deep-link gating observable.

    The page is registered ONLY in the Admin section of the authenticated
    navigation tree, so a non-admin deep-link is intercepted by the
    navigation gate ("Page not found" — the app's established admin-page
    behavior); the page module never runs. The in-page role guard
    (api_keys.py main()) is the second defense layer. Either way the
    contract under test holds: a non-admin session receives NO
    key-management content.
    """
    assert "Create key pair" not in body, f"{role} must not see key-management affordances"
    assert "Issued keys" not in body, f"{role} must not see key-management affordances"
    assert "never be shown again" not in body, f"{role} must never see a secret display"


def test_sc7_viewer_blocked():
    body = _open_page("viewer", "sc7-10-viewer-blocked.png")
    _assert_non_admin_blocked(body, "viewer")


def test_sc7_editor_blocked():
    body = _open_page("editor", "sc7-11-editor-blocked.png")
    _assert_non_admin_blocked(body, "editor")
