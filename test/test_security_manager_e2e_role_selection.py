"""Issue #1379 R-15 — TEST-ONLY role selection for the SNEA_E2E bypass.

SC-10 needs per-role (viewer/editor/admin) authenticated Playwright sessions.
The bypass in src/services/security_manager.py honors SNEA_E2E_ROLE — but
ONLY inside the SNEA_E2E=1 branch: with SNEA_E2E unset the variable is never
read and the production auth path stays byte-identical (the #1400 SC-11a
invariant, re-asserted by test_security_manager_e2e_bypass_inert_sc11a_red.py
and by test_e2e_role_var_inert_without_snea_e2e here).

The role itself is never hardcoded: each role's simulated team maps to a real
seeded Permission row (scripts/seed_permissions.py), so
SecurityManager.get_user_role resolves it through the production RBAC path.

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

import pytest

streamlit = pytest.importorskip("streamlit")

from src.services import security_manager  # noqa: E402
from src.services.security_manager import (  # noqa: E402
    E2E_ROLE_ENV_VAR,
    _e2e_simulated_teams,
)


class _NoTokenController:
    """Cookie controller with NO saved gh_auth_token cookie."""

    def get(self, name):
        return None


class _SessionState(dict):
    """Dict that also supports attribute-style writes, mirroring the real
    streamlit session_state interface used by production code."""

    def __setattr__(self, name, value):
        self[name] = value


def _rehydrate(monkeypatch, snea_e2e=None, snea_e2e_role=None):
    monkeypatch.delenv("SNEA_E2E", raising=False)
    monkeypatch.delenv(E2E_ROLE_ENV_VAR, raising=False)
    if snea_e2e is not None:
        monkeypatch.setenv("SNEA_E2E", snea_e2e)
    if snea_e2e_role is not None:
        monkeypatch.setenv(E2E_ROLE_ENV_VAR, snea_e2e_role)
    monkeypatch.setattr(streamlit, "session_state", _SessionState())
    streamlit.session_state["cookie_controller"] = _NoTokenController()
    security_manager.SecurityManager.rehydrate_session()
    return streamlit.session_state


def test_e2e_role_var_inert_without_snea_e2e(monkeypatch):
    """R-15 hard invariant: with SNEA_E2E unset, SNEA_E2E_ROLE is ignored —
    no authenticated session, no bypass branch, production path unchanged
    even when a role variable is present in the environment."""
    session = _rehydrate(monkeypatch, snea_e2e=None, snea_e2e_role="viewer")
    assert "auth" not in session, "role var must not engage the bypass without SNEA_E2E=1"
    assert "logged_in" not in session
    assert "user_teams" not in session


def test_bypass_default_teams_unchanged(monkeypatch):
    """With SNEA_E2E=1 and no role override, the bypass session carries the
    historical default teams (editor + admin) — existing E2E flows (e.g. the
    #36 admin backfill click-through) must keep resolving admin."""
    session = _rehydrate(monkeypatch, snea_e2e="1", snea_e2e_role=None)
    assert session.get("logged_in") is True
    slugs = sorted(t["slug"] for t in session["user_teams"])
    assert slugs == ["proto-SNEA", "proto-SNEA-admin"]


def test_bypass_role_viewer(monkeypatch):
    """SNEA_E2E_ROLE=viewer swaps the bypass session to the viewer team,
    which the real RBAC path resolves to the viewer role."""
    session = _rehydrate(monkeypatch, snea_e2e="1", snea_e2e_role="viewer")
    slugs = [t["slug"] for t in session["user_teams"]]
    assert slugs == ["proto-SNEA-viewer"]


def test_bypass_role_editor(monkeypatch):
    """SNEA_E2E_ROLE=editor swaps the bypass session to the editor team."""
    session = _rehydrate(monkeypatch, snea_e2e="1", snea_e2e_role="editor")
    slugs = [t["slug"] for t in session["user_teams"]]
    assert slugs == ["proto-SNEA"]


def test_bypass_role_admin(monkeypatch):
    """SNEA_E2E_ROLE=admin explicitly selects the admin-resolving teams."""
    session = _rehydrate(monkeypatch, snea_e2e="1", snea_e2e_role="admin")
    slugs = sorted(t["slug"] for t in session["user_teams"])
    assert slugs == ["proto-SNEA", "proto-SNEA-admin"]


def test_bypass_unknown_role_falls_back_to_default(monkeypatch):
    """An unrecognized SNEA_E2E_ROLE value must not crash the bypass — it
    falls back to the default teams."""
    session = _rehydrate(monkeypatch, snea_e2e="1", snea_e2e_role="bogus")
    slugs = sorted(t["slug"] for t in session["user_teams"])
    assert slugs == ["proto-SNEA", "proto-SNEA-admin"]


def test_e2e_simulated_teams_helper_is_role_pure():
    """The team-selection helper derives teams purely from the override value
    (no session, no DB access) — viewer/editor/admin mapping is explicit."""
    assert [t["slug"] for t in _e2e_simulated_teams("viewer")] == ["proto-SNEA-viewer"]
    assert [t["slug"] for t in _e2e_simulated_teams("editor")] == ["proto-SNEA"]
    assert sorted(t["slug"] for t in _e2e_simulated_teams("admin")) == [
        "proto-SNEA",
        "proto-SNEA-admin",
    ]
    assert sorted(t["slug"] for t in _e2e_simulated_teams(None)) == [
        "proto-SNEA",
        "proto-SNEA-admin",
    ]
