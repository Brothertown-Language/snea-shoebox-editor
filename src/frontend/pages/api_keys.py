# Copyright (c) 2026 Brothertown Language
# <!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
"""
API Keys admin view (issue #1420).

Admin-gated page for managing key+secret pairs that authenticate requests to
the agent-facing read-only records API (``GET /api/v1/records``).

Secret discipline: the plaintext secret is displayed EXACTLY ONCE at
issuance/regeneration and is never redisplayable afterwards — only the
PBKDF2 hash is stored.
"""

import streamlit as st

from src.database.models.api_keys import ApiKeys
from src.logging_config import get_logger
from src.services.api_key_service import ApiKeyService

logger = get_logger("snea.page.api_keys")

_SESSION_NEW_SECRET = "api_keys_new_secret"  # (key, plaintext_secret) shown once
_SESSION_CONFIRM_REVOKE = "api_keys_confirm_revoke"  # key pending revoke confirmation


def _acting_admin() -> str:
    """Identity of the acting admin for audit attribution."""
    user_info = st.session_state.get("user_info") or {}
    return user_info.get("login") or st.session_state.get("user_email") or "unknown"


def _api_base_url() -> str:
    """Best-effort base URL for the copyable request example.

    Derived from the browser request's Host header (what the admin actually
    used to reach the app), with the protocol taken from the platform's
    forwarded-proto header when present (HTTPS on Community Cloud) — so the
    generated command is correct both locally and in production.
    """
    try:
        host = st.context.headers.get("Host") or "localhost:8501"
        proto = st.context.headers.get("X-Forwarded-Proto") or "http"
        return f"{proto}://{host}"
    except Exception:
        return "http://localhost:8501"


def _status_of(row: ApiKeys) -> str:
    if row.revoked_at is not None:
        return "revoked"
    return "enabled" if row.enabled else "disabled"


def main():
    from src.frontend.ui_utils import apply_standard_layout_css, hide_sidebar_nav, render_back_to_main_button

    # Role guard — only admin
    user_role = st.session_state.get("user_role")
    if user_role != "admin":
        st.error("You do not have permission to access this page. Admin role required.")
        return

    hide_sidebar_nav()
    apply_standard_layout_css()

    # ── Sidebar: header and back navigation ───────────────────────
    # Established admin-page pattern (batch_rollback, system_status): the
    # hidden nav is replaced by a titled sidebar rail carrying the back
    # button — never a blank left pane.
    with st.sidebar:
        st.markdown("**API Keys**")
        st.divider()
        render_back_to_main_button()

    st.title("🔑 API Keys")
    st.caption(
        "Credentials for the agent-facing read-only API. Requests authenticate with the "
        "`X-API-Key` and `X-API-Secret` headers. Secrets are stored hashed and are shown "
        "exactly once — at issuance or regeneration."
    )

    # ── One-time secret display ────────────────────────────────────
    pending = st.session_state.get(_SESSION_NEW_SECRET)
    if pending:
        key, secret = pending
        st.success(f"New secret issued for `{key}`. **Copy it now — it will never be shown again.**")
        st.code(secret, language=None)
        st.caption("Copyable request (same one-time display — the command embeds the secret):")
        st.code(
            f'curl -sS -H "X-API-Key: {key}" -H "X-API-Secret: {secret}" '
            f'"{_api_base_url()}/api/v1/records" -o records.json',
            language="bash",
        )
        if st.button("I have stored the secret", key="api_keys_ack_secret"):
            del st.session_state[_SESSION_NEW_SECRET]
            st.rerun()

    # ── Create key pair ────────────────────────────────────────────
    with st.form("api_keys_create", clear_on_submit=True):
        st.subheader("Create key pair")
        label = st.text_input("Label", placeholder="e.g. downstream analysis agent")
        submitted = st.form_submit_button("Create", type="primary")
        if submitted:
            if not label.strip():
                st.error("A label is required.")
            else:
                try:
                    key, secret = ApiKeyService.create_key(label.strip(), _acting_admin())
                    st.session_state[_SESSION_NEW_SECRET] = (key, secret)
                    st.rerun()
                except Exception as e:
                    logger.error("API key creation failed: %s", e)
                    st.error("Creating the key failed. Please try again.")

    # ── Key list with lifecycle actions ────────────────────────────
    st.subheader("Issued keys")
    try:
        keys = ApiKeyService.list_keys()
    except Exception as e:
        logger.error("API key listing failed: %s", e)
        st.error("Loading the key list failed. Please try again.")
        return

    if not keys:
        st.info("No API keys have been issued yet.")
        return

    for row in keys:
        status = _status_of(row)
        with st.container(border=True):
            head_left, head_right = st.columns([3, 1])
            head_left.markdown(f"**{row.label or '(no label)'}** — `{row.key}`")
            head_right.markdown(f"**{status}**")
            created = row.created_at.strftime("%Y-%m-%d %H:%M UTC") if row.created_at else "—"
            last_used = row.last_used_at.strftime("%Y-%m-%d %H:%M UTC") if row.last_used_at else "never"
            st.caption(f"created {created} by {row.created_by or '—'} · last used {last_used}")

            act1, act2, act3 = st.columns(3)
            if act2.button(
                "Enable" if not row.enabled else "Disable",
                key=f"toggle_{row.key}",
                disabled=row.revoked_at is not None,
            ):
                if ApiKeyService.set_enabled(row.key, not row.enabled, _acting_admin()):
                    st.rerun()

            confirm_key = f"confirm_revoke_{row.key}"
            if act3.button("Revoke", key=f"revoke_{row.key}", disabled=row.revoked_at is not None):
                st.session_state[confirm_key] = True
                st.rerun()
            if st.session_state.get(confirm_key):
                st.warning(f"Revoke `{row.key}`? Requests with this key will be rejected (403).")
                yes, no = st.columns(2)
                if yes.button("Confirm revoke", key=f"confirm_{row.key}", type="primary"):
                    if ApiKeyService.revoke_key(row.key, _acting_admin()):
                        st.session_state.pop(confirm_key, None)
                        st.rerun()
                if no.button("Cancel", key=f"cancel_{row.key}"):
                    st.session_state.pop(confirm_key, None)
                    st.rerun()

            if act1.button("Regenerate secret", key=f"regen_{row.key}", disabled=row.revoked_at is not None):
                try:
                    secret = ApiKeyService.regenerate_secret(row.key, _acting_admin())
                    if secret is not None:
                        st.session_state[_SESSION_NEW_SECRET] = (row.key, secret)
                        st.rerun()
                except Exception as e:
                    logger.error("API key regeneration failed: %s", e)
                    st.error("Regenerating the secret failed. Please try again.")


if __name__ == "__main__":
    main()
