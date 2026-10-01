"""Enforcement test for SC-SC8 (issue 1392): local-run auth-state simulation hook.

SC-8: env var SNEA_SIMULATE_AUTH (values: authorized | unauthorized | anonymous)
is honored by the app's identity path ONLY when the secrets [runtime] mode equals
"local"; inert in production mode.

Values map to identity-path outcomes:
- "authorized"    -> successful identity (session identity synchronized)
- "unauthorized"  -> st.session_state["is_unauthorized"] is True, sync returns False
- "anonymous"     -> unauthenticated outcome (no identity data, no unauthorized flag)

All tests MUST FAIL against current code (RED phase): no simulation hook exists.

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

from unittest.mock import MagicMock

import pytest

streamlit = pytest.importorskip("streamlit")

import src.services.identity_service as identity_service  # noqa: E402

HOOK_ENV_VAR = "SNEA_SIMULATE_AUTH"


class FakeSecrets:
    """Minimal st.secrets stand-in supporting [runtime] and [github_oauth]."""

    def __init__(self, runtime_mode):
        self._data = {
            "runtime": {"mode": runtime_mode},
            "github_oauth": {
                "client_id": "test-client-id",
                "client_secret": "test-client-secret",
                "authorize_url": "https://example.com/authorize",
                "token_url": "https://example.com/token",
                "redirect_uri": "https://example.com/redirect",
                "user_info_url": "https://example.com/user",
            },
        }

    def __contains__(self, key):
        return key in self._data

    def __getitem__(self, key):
        return self._data[key]


def _install_streamlit_fakes(monkeypatch, runtime_mode):
    """Replace st.secrets / st.session_state / UI surfaces so identity path is testable."""
    monkeypatch.setattr(streamlit, "secrets", FakeSecrets(runtime_mode))
    monkeypatch.setattr(streamlit, "session_state", {})
    monkeypatch.setattr(streamlit, "error", lambda *a, **k: None)
    monkeypatch.setattr(streamlit, "warning", lambda *a, **k: None)
    monkeypatch.setattr(streamlit, "success", lambda *a, **k: None)


def _install_error_recorder(monkeypatch):
    """Track st.error calls so vacuous exception-path outcomes are detected."""
    errors: list[str] = []
    monkeypatch.setattr(streamlit, "error", lambda msg, *a, **k: errors.append(str(msg)))
    return errors


def _forbid_network(monkeypatch):
    """Any GitHub HTTP call during simulation is a test failure."""

    def _no_network(*args, **kwargs):
        raise AssertionError("network access attempted during auth simulation")

    monkeypatch.setattr("src.services.identity_service.requests.get", _no_network)


# SC-SC8 assertion (1): the identity path exposes the simulation hook keyed on
# SNEA_SIMULATE_AUTH with values authorized/unauthorized/anonymous.
def test_sc8_simulation_hook_is_exposed():
    from src.services.identity_service import resolve_simulated_auth  # noqa: F401


# SC-SC8 assertion (2): the hook is gated on [runtime] mode == "local" —
# when mode is production the variable is ignored.
def test_sc8_hook_gated_on_local_mode(monkeypatch):
    from src.services.identity_service import resolve_simulated_auth

    monkeypatch.setenv(HOOK_ENV_VAR, "authorized")

    # Production mode: variable must be ignored.
    _install_streamlit_fakes(monkeypatch, "production")
    assert resolve_simulated_auth() is None, (
        "SNEA_SIMULATE_AUTH must be ignored when [runtime] mode is production"
    )

    # Local mode: variable must be honored.
    _install_streamlit_fakes(monkeypatch, "local")
    assert resolve_simulated_auth() == "authorized"
    assert resolve_simulated_auth.__module__ == "src.services.identity_service"


# SC-SC8 assertion (3): value mapping through the identity path.
def test_sc8_unauthorized_value_produces_is_unauthorized_outcome(monkeypatch):
    from src.services.identity_service import IdentityService

    _install_streamlit_fakes(monkeypatch, "local")
    _forbid_network(monkeypatch)
    monkeypatch.setenv(HOOK_ENV_VAR, "unauthorized")

    result = IdentityService.sync_identity("fake-token")
    assert result is False
    assert streamlit.session_state.get("is_unauthorized") is True


def test_sc8_authorized_value_produces_successful_identity(monkeypatch):
    from src.services.identity_service import IdentityService

    _install_streamlit_fakes(monkeypatch, "local")
    _forbid_network(monkeypatch)
    monkeypatch.setenv(HOOK_ENV_VAR, "authorized")

    # DB sync is not part of this SC; stub it out so the simulation path alone is tested.
    monkeypatch.setattr(
        identity_service.IdentityService, "sync_user_to_db", MagicMock()
    )

    result = IdentityService.sync_identity("fake-token")
    assert result is True
    state = streamlit.session_state
    assert "user_info" in state and "user_orgs" in state and "user_teams" in state
    assert state.get("user_role"), "authorized simulation must populate user_role"


def test_sc8_anonymous_value_produces_unauthenticated_outcome(monkeypatch):
    from src.services.identity_service import IdentityService

    _install_streamlit_fakes(monkeypatch, "local")
    _forbid_network(monkeypatch)
    monkeypatch.setenv(HOOK_ENV_VAR, "anonymous")
    errors = _install_error_recorder(monkeypatch)

    result = IdentityService.sync_identity("fake-token")
    state = streamlit.session_state
    assert result is False
    assert not errors, (
        "anonymous simulation must short-circuit cleanly, not fall through the "
        f"exception/error path: {errors}"
    )
    assert "user_info" not in state, "anonymous must not populate identity data"
    assert "is_unauthorized" not in state, (
        "anonymous is unauthenticated, not unauthorized"
    )
