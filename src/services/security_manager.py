# Copyright (c) 2026 Brothertown Language
# <!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
import os
from typing import Any

import streamlit as st

from src.database.connection import get_session
from src.database.models.identity import Permission
from src.frontend.constants import GH_AUTH_TOKEN_COOKIE
from src.logging_config import get_logger

logger = get_logger("snea.security")

# TEST-ONLY (Issue #1400 SC-11): clearly-marked synthetic access token for the
# SNEA_E2E-gated auth bypass. This is NOT a credential — it is never sent to
# GitHub and is only accepted when SNEA_E2E=1 (unreachable in production).
E2E_TEST_ONLY_SYNTHETIC_TOKEN = "snea-e2e-TEST-ONLY-synthetic-identity-not-a-credential"

# TEST-ONLY (Issue #1379 R-15): role-selection variable for the SNEA_E2E
# bypass. Read exclusively inside the SNEA_E2E=1 branch — with SNEA_E2E unset
# the variable is never read and the production auth path is byte-identical.
E2E_ROLE_ENV_VAR = "SNEA_E2E_ROLE"

# TEST-ONLY viewer team mirroring the real permission seed
# (scripts/seed_permissions.py: proto-SNEA-viewer -> viewer).
_E2E_VIEWER_TEAM = {
    "slug": "proto-SNEA-viewer",
    "name": "proto-SNEA-viewer",
    "organization": {"login": "Brothertown-Language"},
}


def _e2e_simulated_teams(role_override: str | None) -> list[dict[str, Any]]:
    """TEST-ONLY bypass session teams, selected by SNEA_E2E_ROLE.

    Unset or 'admin' keeps the historical default (editor + admin teams, so
    the real RBAC path resolves admin and existing E2E flows are unchanged).
    'viewer'/'editor' swap in the matching seed-permission team so per-role
    E2E flows resolve their role through get_user_role's real DB walk — the
    role is never hardcoded. Any other value falls back to the default.
    """
    from src.services.identity_service import _SIMULATED_USER_TEAMS

    editor_teams = [dict(t) for t in _SIMULATED_USER_TEAMS]
    admin_team = {
        "slug": "proto-SNEA-admin",
        "name": "proto-SNEA-admin",
        "organization": {"login": "Brothertown-Language"},
    }
    if role_override == "viewer":
        return [dict(_E2E_VIEWER_TEAM)]
    if role_override == "editor":
        return editor_teams
    return editor_teams + [admin_team]


class SecurityManager:
    """
    Centralized service for RBAC, session rehydration, and route protection.
    """

    @staticmethod
    def rehydrate_session():
        """
        Extract cookie-based rehydration logic from streamlit_app.py.
        """
        if "cookie_controller" not in st.session_state:
            return

        # Issue #1400 precedence: the SNEA_SIMULATE_AUTH local-mode hook
        # resolves BEFORE the SNEA_E2E test bypass. Legacy tests that
        # restart the app with a simulated value get that state
        # (unauthorized/anonymous semantics applied downstream by
        # IdentityService.sync_identity via the normal cookie path); only
        # when the hook resolves None does the TEST-ONLY bypass apply.
        from src.services.identity_service import resolve_simulated_auth

        simulated = resolve_simulated_auth()
        if simulated is not None:
            logger.warning(
                "SNEA_SIMULATE_AUTH=%s resolved — SNEA_E2E test bypass not engaged.",
                simulated,
            )
        # TEST-ONLY auth bypass hook (Issue #1400 SC-11): when SNEA_E2E=1 is
        # set in the environment, short-circuit session-token establishment —
        # establish an authenticated test session with a clearly-marked
        # synthetic identity, without any real GitHub token or headed login.
        # Unreachable in production (SNEA_E2E is unset), so real production
        # auth behavior is unchanged.
        elif os.environ.get("SNEA_E2E") == "1" and "auth" not in st.session_state:
            logger.warning(
                "TEST-ONLY auth bypass engaged (SNEA_E2E=1): establishing a "
                "synthetic authenticated session — not a real credential."
            )
            st.session_state["auth"] = {
                "token": {"access_token": E2E_TEST_ONLY_SYNTHETIC_TOKEN},
                "test_only": True,
            }
            st.session_state["logged_in"] = True
            # Seed the identity keys so IdentityService.sync_identity()
            # short-circuits via is_identity_synchronized() and never contacts
            # GitHub with the synthetic token. Reuses the simulated identity
            # constants from identity_service (test-only data).
            from src.services.identity_service import (
                _SIMULATED_USER_INFO,
                _SIMULATED_USER_ORGS,
                _SIMULATED_USER_TEAMS,
                IdentityService,
            )

            st.session_state["user_info"] = dict(_SIMULATED_USER_INFO)
            st.session_state["user_orgs"] = [dict(o) for o in _SIMULATED_USER_ORGS]
            # The E2E harness must exercise BOTH role tiers (admin backfill
            # click-through SC-13 + editor-level flows), so the default bypass
            # session carries the admin team from the real permission seed
            # (scripts/seed_permissions.py: proto-SNEA-admin -> admin) in
            # addition to the simulated editor team; the role is derived
            # through the real RBAC path, never hardcoded.
            # Issue #1379 R-15: SNEA_E2E_ROLE (read ONLY here, under
            # SNEA_E2E=1) lets a test select viewer/editor/admin by swapping
            # the simulated teams; with SNEA_E2E unset this line is never
            # reached and production auth is byte-identical.
            role_override = os.environ.get(E2E_ROLE_ENV_VAR)
            if role_override not in (None, "viewer", "editor", "admin"):
                logger.warning(
                    "TEST-ONLY %s=%r unrecognized — falling back to the default bypass teams.",
                    E2E_ROLE_ENV_VAR,
                    role_override,
                )
            st.session_state["user_teams"] = _e2e_simulated_teams(role_override)
            # user_role is deliberately NOT seeded here: the app derives it
            # lazily from user_teams via SecurityManager.get_user_role()
            # (streamlit_app navigation block), exercising the real RBAC
            # path — proto-SNEA-admin resolves to admin, proto-SNEA to editor.
            st.session_state["user_email"] = "e2e-test-only-synthetic@invalid"
            # Mirror the real identity path (fetch_github_user_info ->
            # sync_user_to_db): create the test-only user record so
            # FK-backed persistence (e.g. user_preferences.user_email)
            # works for the bypass session exactly as for a real login.
            # DB access is gated on a live Streamlit script-run context so
            # bare unit-test invocations (no app runtime) stay inert.
            from streamlit.runtime.scriptrunner import get_script_run_ctx

            if get_script_run_ctx() is not None:
                IdentityService.sync_user_to_db(_SIMULATED_USER_INFO, st.session_state["user_email"])
            return

        controller = st.session_state["cookie_controller"]
        try:
            saved_token = controller.get(GH_AUTH_TOKEN_COOKIE)
        except TypeError:
            return

        if saved_token and "auth" not in st.session_state:
            logger.debug("Rehydrating session from saved cookie token")
            st.session_state["auth"] = saved_token
            st.session_state.logged_in = True

    @staticmethod
    def get_user_role(user_teams: list[dict[str, Any]]) -> str | None:
        """
        Resolve the highest global role for a user based on their GitHub teams.
        """
        # Roles hierarchy: admin > editor > viewer
        role_hierarchy = {"admin": 3, "editor": 2, "viewer": 1}
        highest_role = None
        highest_weight = 0

        logger.debug("Resolving role for %d team(s)", len(user_teams))
        session = get_session()
        try:
            # Fetch all permissions from DB
            permissions = session.query(Permission).all()
            logger.debug("Loaded %d permission rule(s) from DB", len(permissions))

            for p in permissions:
                # Check if user is in the required team and org
                match = False
                for team in user_teams:
                    team_slug = team.get("slug")
                    # Use team slug or name for matching (slug is more reliable)
                    team_identifier = team_slug or team.get("name")
                    org_login = team.get("organization", {}).get("login")

                    if p.github_team.lower() == team_identifier.lower() and p.github_org.lower() == org_login.lower():
                        match = True
                        break

                if match:
                    weight = role_hierarchy.get(p.role, 0)
                    if weight > highest_weight:
                        highest_weight = weight
                        highest_role = p.role

            logger.debug("Resolved role: %s", highest_role)
            return highest_role
        except Exception as e:
            logger.error("get_user_role failed: %s", e)
            return None
        finally:
            session.close()

    @staticmethod
    def check_permission(user_email: str, source_id: int | None, required_role: str) -> bool:
        """
        Check if a user has the required role for a specific source.
        If source_id is None, it checks for any permission matching the role.
        """
        role_hierarchy = {"admin": 3, "editor": 2, "viewer": 1}
        required_weight = role_hierarchy.get(required_role, 0)

        if "user_teams" not in st.session_state:
            return False

        user_teams = st.session_state["user_teams"]

        session = get_session()
        try:
            # Query permissions that match the user's teams/orgs
            # and satisfy the source_id (either specific or global)

            permissions = session.query(Permission).all()

            user_max_weight = 0
            for p in permissions:
                # Check source compatibility
                if source_id is not None and p.source_id is not None and p.source_id != source_id:
                    continue

                # Check team membership
                match = False
                for team in user_teams:
                    team_slug = team.get("slug")
                    team_identifier = team_slug or team.get("name")
                    org_login = team.get("organization", {}).get("login")

                    if p.github_team.lower() == team_identifier.lower() and p.github_org.lower() == org_login.lower():
                        match = True
                        break

                if match:
                    user_max_weight = max(user_max_weight, role_hierarchy.get(p.role, 0))

            return user_max_weight >= required_weight
        except Exception as e:
            logger.error("check_permission failed: %s", e)
            return False
        finally:
            session.close()
