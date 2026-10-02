"""Issue #1400 SC-11a — RED: SNEA_E2E-gated auth bypass INERT when unset.

SC-11a: with `SNEA_E2E` unset, the auth resolution in
src/services/security_manager.py follows the production path — the bypass
branch is NOT taken, no authenticated session is established from the bypass,
and no synthetic token is injected. Behavior is identical to the pre-bypass
production baseline.

Expected outcome (RED plan item 13): the test FAILS if the bypass branch is
reachable with SNEA_E2E unset or if the synthetic token leaks into the
session. If the bypass is already strictly gated behind `SNEA_E2E == "1"`,
the test passes immediately and the RED abort protocol classifies
ALREADY_GREEN — reported honestly, not forced.

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

import pytest

streamlit = pytest.importorskip("streamlit")

from src.services import security_manager  # noqa: E402
from src.services.security_manager import (  # noqa: E402
    E2E_TEST_ONLY_SYNTHETIC_TOKEN,
)


class _NoTokenController:
    """Cookie controller with NO saved gh_auth_token cookie."""

    def get(self, name):
        return None


class _SavedTokenController:
    """Cookie controller with a saved production cookie token."""

    def __init__(self, token):
        self._token = token

    def get(self, name):
        return self._token


class _SessionState(dict):
    """Dict that also supports attribute-style writes, mirroring the real
    streamlit session_state interface used by production code."""

    def __setattr__(self, name, value):
        self[name] = value


def _reset_session(monkeypatch):
    monkeypatch.setattr(streamlit, "session_state", _SessionState())


def test_sc11a_no_bypass_no_auth_without_snea_e2e(monkeypatch):
    """With SNEA_E2E unset and no saved cookie token, the auth resolution
    must NOT establish any authenticated session state (no bypass branch,
    no synthetic token injected)."""
    monkeypatch.delenv("SNEA_E2E", raising=False)
    _reset_session(monkeypatch)
    streamlit.session_state["cookie_controller"] = _NoTokenController()

    security_manager.SecurityManager.rehydrate_session()

    assert "auth" not in streamlit.session_state, (
        "SC-11a: with SNEA_E2E unset, a session was established without a "
        "saved cookie token — the bypass branch was taken in production "
        "conditions."
    )
    assert "logged_in" not in streamlit.session_state, (
        "SC-11a: with SNEA_E2E unset, the session was marked logged_in "
        "without a saved cookie token — bypass leak into production path."
    )


def test_sc11a_no_synthetic_token_when_snea_e2e_unset(monkeypatch):
    """With SNEA_E2E unset, the synthetic test-only token must never appear
    in session state regardless of cookie contents."""
    monkeypatch.delenv("SNEA_E2E", raising=False)
    _reset_session(monkeypatch)
    streamlit.session_state["cookie_controller"] = _SavedTokenController(
        "real-production-cookie-token"
    )

    security_manager.SecurityManager.rehydrate_session()

    auth = streamlit.session_state.get("auth")
    if auth is not None:
        assert auth != E2E_TEST_ONLY_SYNTHETIC_TOKEN, (
            "SC-11a: synthetic test-only token leaked into the auth session "
            "state with SNEA_E2E unset."
        )
        assert auth.get("test_only") is not True if isinstance(
            auth, dict
        ) else True, (
            "SC-11a: test-only bypass session marker present with SNEA_E2E "
            "unset — bypass branch taken in production conditions."
        )


def test_sc11a_production_cookie_rehydration_unchanged_when_snea_e2e_unset(monkeypatch):
    """With SNEA_E2E unset, a saved cookie token must rehydrate exactly as in
    the pre-bypass production baseline: auth set to the saved token value and
    logged_in True — identical to pre-bypass production behavior."""
    monkeypatch.delenv("SNEA_E2E", raising=False)
    _reset_session(monkeypatch)
    streamlit.session_state["cookie_controller"] = _SavedTokenController(
        "real-production-cookie-token"
    )

    security_manager.SecurityManager.rehydrate_session()

    assert streamlit.session_state.get("auth") == "real-production-cookie-token", (
        "SC-11a: production cookie rehydration behavior changed — auth "
        "session state does not match the pre-bypass production baseline."
    )
    assert streamlit.session_state.get("logged_in") is True, (
        "SC-11a: production cookie rehydration did not mark the session "
        "logged_in — divergence from the pre-bypass production baseline."
    )