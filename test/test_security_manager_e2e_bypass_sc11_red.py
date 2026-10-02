"""Issue #1400 SC-11 — RED: SNEA_E2E-gated auth bypass hook engagement.

SC-11: the pinned test-only auth bypass hook exists in the app's auth path
(src/services/security_manager.py auth resolution) and ENGAGES the auth
resolution when SNEA_E2E=1: with the gate set, SecurityManager.rehydrate_session
establishes an authenticated session state (auth token + logged_in) WITHOUT
any saved cookie token — no headed OAuth login, no fabricated credentials.

Expected to FAIL (RED): no bypass hook exists yet — with no saved token the
auth resolution performs no session establishment at all.

(Inertness when SNEA_E2E is UNSET is SC-11a / plan Item 13 — NOT tested here.)

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

import pytest

streamlit = pytest.importorskip("streamlit")

from src.services import security_manager  # noqa: E402


def test_sc11_bypass_hook_engages_auth_resolution_with_snea_e2e(monkeypatch):
    """With SNEA_E2E=1 and NO saved cookie token, the auth resolution must
    establish an authenticated session state via the test-only bypass hook."""
    monkeypatch.setenv("SNEA_E2E", "1")
    monkeypatch.setattr(streamlit, "session_state", {})

    class _NoTokenController:
        """Cookie controller with NO saved gh_auth_token cookie."""

        def get(self, name):
            return None

    streamlit.session_state["cookie_controller"] = _NoTokenController()

    security_manager.SecurityManager.rehydrate_session()

    assert streamlit.session_state.get("auth"), (
        "SC-11 RED: SNEA_E2E=1 auth bypass hook does not exist yet — "
        "SecurityManager.rehydrate_session established no authenticated "
        "session state without a saved cookie token."
    )
    assert streamlit.session_state.get("logged_in") is True, (
        "SC-11 RED: SNEA_E2E=1 auth bypass hook did not mark the session "
        "logged_in — bypass hook missing from the auth resolution."
    )