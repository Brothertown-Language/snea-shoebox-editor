# Copyright (c) 2026 Brothertown Language
"""
UI utilities for Streamlit components.
"""
import time
from typing import Dict

import streamlit as st
import streamlit.components.v1 as components
from src.frontend.constants import GH_AUTH_TOKEN_COOKIE


# ── Infrastructure Dialogs ─────────────────────────────────────────────


@st.dialog("Database Starting")
def show_startup_dialog(config: Dict[str, str], initial_status: str):
    """Display a dialog with the database startup status."""
    from src.services.infrastructure_service import InfrastructureService

    st.write(f"The production database is currently **{initial_status}**.")

    if initial_status == "POWEROFF":
        st.write("Sending start command...")
        if not InfrastructureService.start_service(config):
            st.error("Failed to send start command. Please contact support.")
            return
        st.write("Start command sent. Waiting for database to become active...")

    max_polls = 60
    poll_delay = 10

    status_placeholder = st.empty()
    progress_bar = st.progress(0)

    current_status = initial_status
    for i in range(max_polls):
        current_status = InfrastructureService.get_service_status(config)

        dns_ok = True
        if current_status == "RUNNING":
            from urllib.parse import urlparse
            from src.database import get_db_url
            url = get_db_url()
            if url:
                parsed = urlparse(url)
                host = parsed.hostname
                if host:
                    dns_ok, _, _, _ = InfrastructureService.verify_dns(host)

        if current_status == "RUNNING" and dns_ok:
            status_placeholder.success("Database is now online!")
            progress_bar.progress(100)
            time.sleep(2)
            st.rerun()
            return

        display_status = current_status
        if current_status == "RUNNING" and not dns_ok:
            display_status = "RUNNING (Waiting for DNS)"

        status_placeholder.info(
            f"Current Status: **{display_status or 'Unknown'}**\n\n"
            f"Checking again in {poll_delay}s... (Attempt {i+1}/{max_polls})"
        )
        progress_bar.progress((i + 1) / max_polls)
        time.sleep(poll_delay)

    if current_status == "REBUILDING":
        st.rerun()

    st.error("The production database is taking too long to start. Please try refreshing the page in a few minutes.")


@st.dialog("Missing Secrets")
def show_secrets_missing_dialog(missing_secrets: list[str]):
    """Display a dialog listing missing mandatory secrets."""
    st.error("The application cannot start because one or more mandatory secrets are missing.")
    st.write("Please ensure the following secrets are configured in Streamlit Cloud or `.streamlit/secrets.toml`:")
    for secret in missing_secrets:
        st.markdown(f"- `{secret}`")

    st.info("After adding the secrets, please refresh the page.")
    if st.button("I've added the secrets, refresh now"):
        st.rerun()


def ensure_secrets_present():
    """Verify that all mandatory secrets are present. Blocks execution if any are missing."""
    from src.services.infrastructure_service import InfrastructureService

    missing = InfrastructureService.get_missing_secrets()
    if missing:
        show_secrets_missing_dialog(missing)
        st.stop()


def ensure_db_alive():
    """Check if DB is alive, start it if not, and show dialog until ready."""
    from src.services.infrastructure_service import InfrastructureService

    is_alive, status = InfrastructureService.check_db_alive()
    if is_alive:
        return

    config = InfrastructureService.get_aiven_config()
    if not config:
        return

    if status in ["POWEROFF", "REBUILDING", "STARTING_DNS"]:
        show_startup_dialog(config, "STARTING" if status == "STARTING_DNS" else status)
        st.stop()
    else:
        st.warning(f"Database is in an unexpected state: {status}. Access is blocked for safety.")
        st.stop()


# ── Page Utilities ─────────────────────────────────────────────────────


def reload_page_at_root(delay_ms: int = 0) -> None:
    js_code = f"""
        <script>
            // Clear the auth cookie
            document.cookie = "{GH_AUTH_TOKEN_COOKIE}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
            document.cookie = "{GH_AUTH_TOKEN_COOKIE}=; expires=Thu, 01 Jan 1970 00:00:00 UTC;";

            function reloadPageAtRoot() {{
                try {{
                    // Navigate the TOP-LEVEL window, not the iframe
                    window.top.location.href = "/";
                }} catch (e) {{
                    // Fallback: force top-level reload
                    window.top.location.reload();
                }}
            }}

            {f"setTimeout(reloadPageAtRoot, {delay_ms});" if delay_ms > 0 else "reloadPageAtRoot();"}
        </script>
    """
    components.html(js_code, height=0)
