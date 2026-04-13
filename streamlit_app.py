# Copyright (c) 2026 Brothertown Language
# <!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
from __future__ import annotations

import socket
import time as _time
from urllib.parse import urlparse

import streamlit as st

from src.database.connection import get_db_url, init_db, is_production
from src.frontend.ui_utils import hide_sidebar_nav
from src.logging_config import get_logger
from src.services.infrastructure_service import InfrastructureService

logger = get_logger("snea.app")


def _handle_aiven_startup(attempt: int) -> tuple[bool, str, str | None]:
    """Handle Aiven service startup sequence.

    Checks Aiven service status BEFORE DNS resolution and handles POWEROFF state.

    Returns:
        tuple: (should_skip_dns: bool, remote_info: str, error_msg: str | None)
            - should_skip_dns: True if DNS check should be skipped (service starting)
            - remote_info: Status string for logging (e.g., "[remote_state=POWEROFF] [start_sent]")
            - error_msg: Non-None if API call failed and user should see an error dialog
    """
    if not is_production():
        return False, "", None

    config = InfrastructureService.get_aiven_config()
    if not config:
        return False, "", None

    try:
        r_status = InfrastructureService.get_service_status(config)
    except Exception as e:
        logger.error("Failed to get Aiven service status: %s", e)
        return (
            False,
            " [remote_state=unknown]",
            (
                f"Failed to check database status. The Aiven API is unavailable.\n\n"
                f"Error: {e}\n\n"
                "Please try again in a few minutes, or contact support if the problem persists."
            ),
        )

    remote_info = f" [remote_state={r_status or 'unknown'}]"

    if r_status == "POWEROFF":
        if attempt == 1:
            logger.info("Aiven service is POWEROFF. Sending start command...")
            try:
                success = InfrastructureService.start_service(config)
                if not success:
                    logger.error("Aiven start_service() returned False")
                    return (
                        False,
                        remote_info,
                        (
                            "Failed to start the database. The Aiven API accepted the request but "
                            "the start command did not succeed.\n\n"
                            "Please wait a few minutes and refresh the page, or try starting the "
                            "database manually from the Aiven console."
                        ),
                    )
                remote_info += " [start_sent]"
            except Exception as e:
                logger.error("Aiven start_service() raised exception: %s", e)
                return (
                    False,
                    remote_info,
                    (
                        f"Failed to start the database. The Aiven API request failed.\n\n"
                        f"Error: {e}\n\n"
                        "Please check your network connection and try again, or start the database "
                        "manually from the Aiven console."
                    ),
                )
        # Skip DNS check while service is starting - DNS won't resolve yet
        return True, remote_info, None

    if r_status == "STARTING":
        # Skip DNS check while service is starting
        return True, remote_info, None

    # Service is RUNNING or other state - proceed with normal checks including DNS
    return False, remote_info, None


@st.cache_resource
def _initialize_database():
    """Run database initialization once on app startup.

    Retries with exponential back-off to handle transient failures
    (e.g., local PostgreSQL still shutting down). Shows a user-friendly
    spinner and guidance instead of flooding the UI/logs.
    """
    max_attempts = 60
    base_delay = 1.0  # seconds
    max_delay = 10.0  # seconds cap

    with st.spinner("Initializing database…"):
        status = st.empty()
        for attempt in range(1, max_attempts + 1):
            remote_info = ""  # Initialize for local dev; Aiven will override in production
            try:
                # 1. Check Aiven status BEFORE DNS (production only)
                skip_dns, remote_info, aiven_error = _handle_aiven_startup(attempt)

                if aiven_error:
                    # API failure - show error dialog
                    status.empty()
                    st.error("Database startup failed")
                    st.error(aiven_error)

                    mastodon_url = st.secrets.get("contact", {}).get("mastodon_url")
                    if mastodon_url:
                        st.info(
                            f"If the problem persists, please report the issue to "
                            f"Michael Conrad on Mastodon: [{mastodon_url}]({mastodon_url})"
                        )

                    if st.button("Retry initialization"):
                        st.rerun()
                    st.stop()

                if skip_dns:
                    # Aiven is starting - DNS won't resolve yet, raise transient error
                    raise Exception(f"Aiven starting up{remote_info}")

                # 2. DNS Pre-connect check (only when Aiven is RUNNING or local dev)
                db_url = get_db_url()
                if db_url and "://" in db_url:
                    try:
                        parsed = urlparse(db_url)
                        if parsed.hostname and parsed.hostname not in ("localhost", "127.0.0.1"):
                            # This will raise socket.gaierror if DNS fails
                            socket.gethostbyname(parsed.hostname)
                    except socket.gaierror as dns_err:
                        # Re-raise as a generic exception with a message that
                        # matches our transient detection list below.
                        raise Exception(f"DNS Resolution Failed: {dns_err} (Name or service not known)") from dns_err

                # 3. Schema initialization
                init_db()
                status.empty()
                return  # success
            except Exception as e:
                err_msg = str(e).lower()
                is_transient = any(
                    phrase in err_msg
                    for phrase in (
                        "shutting down",
                        "starting up",
                        "the database system is not yet accepting connections",
                        "could not connect to server",
                        "connection refused",
                        "name or service not known",
                        "temporary failure in name resolution",
                        "could not translate host name",
                        "failed to connect to",
                        "connection timed out",
                        "aiven starting up",
                    )
                )

                # Add DNS flag to remote_info if DNS resolution failed
                if "dns resolution failed" in err_msg:
                    remote_info = remote_info + " [dns=not_ready]"

                if is_transient and attempt < max_attempts:
                    delay = min(base_delay * attempt, max_delay)
                    # Log at WARNING as requested, including remote status
                    logger.warning(
                        "DB init transient failure %d/%d:%s %s — retrying in %.1fs",
                        attempt,
                        max_attempts,
                        remote_info,
                        e,
                        delay,
                    )
                    status.info(
                        f"Database is starting up or recovering (attempt {attempt}/{max_attempts}). "
                        f"This is usually temporary, but can take up to 10 minutes for the database to start. "
                        f"Retrying in {delay:.1f}s…"
                    )
                    _time.sleep(delay)
                else:
                    # Final failure: provide actionable guidance without stack spam
                    status.empty()
                    st.error("Database is unavailable. Please try one of the following:")

                    mastodon_url = st.secrets.get("contact", {}).get("mastodon_url")
                    if mastodon_url:
                        st.info(
                            f"If the problem persists, please report the issue to "
                            f"Michael Conrad on Mastodon: [{mastodon_url}]({mastodon_url})"
                        )

                    if st.button("Retry initialization"):
                        st.rerun()

                    with st.expander("Troubleshooting tips"):
                        st.markdown(
                            "- Wait a few seconds and press the R key to refresh the page.\n"
                            "- If running locally, ensure the embedded PostgreSQL can start.\n"
                            "- Advanced: run `scripts/test_db_connection.py` to diagnose connectivity.\n"
                            "- If the problem persists, stop all local Postgres services and restart the app."
                        )
                    # Still log the underlying error at WARNING for operators
                    logger.warning("DB init failed: %s", e)
                    st.stop()


def main():
    # Page configuration MUST be the first Streamlit command
    st.set_page_config(page_title="SNEA Shoebox Editor", page_icon="📚", layout="wide")

    # Initialize database on first load
    _initialize_database()

    # Initialize session state for authentication
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    # 1. Initialize Cookie Controller
    from streamlit_cookies_controller import CookieController

    # Initializing and rendering the controller early
    controller = CookieController()
    st.session_state["cookie_controller"] = controller

    # 2. Rehydrate Session State
    from src.services.security_manager import SecurityManager

    logger.debug("Rehydrating session state from cookies")
    SecurityManager.rehydrate_session()

    # 3. Global Identity Synchronization
    # CRITICAL: This logic must remain in streamlit_app.py to prevent race conditions.
    # By fetching user info (including profile, orgs, and teams) here, we ensure
    # it's available regardless of which page the user lands on first after
    # OAuth or cookie rehydration.
    if "auth" in st.session_state:
        from src.services.identity_service import IdentityService

        access_token = st.session_state["auth"].get("token", {}).get("access_token")
        if access_token:
            logger.debug("Auth token present, syncing identity")
            if not IdentityService.sync_identity(access_token):
                # Handle unauthorized or failed fetch
                if st.session_state.get("is_unauthorized"):
                    # The dialog will be shown below
                    pass
                else:
                    # Generic error — clear auth state and revert to login
                    st.error("Failed to fetch user information.")
                    for key in ["auth", "user_info", "user_orgs", "user_teams", "user_role", "user_email"]:
                        st.session_state.pop(key, None)
                    st.session_state.logged_in = False
                    if "cookie_controller" in st.session_state:
                        from src.frontend.constants import GH_AUTH_TOKEN_COOKIE

                        st.session_state["cookie_controller"].remove(GH_AUTH_TOKEN_COOKIE)
                    st.rerun()

    # Define navigation
    from src.services.navigation_service import NavigationService

    if st.session_state.get("is_unauthorized"):
        from src.frontend.pages.login import show_unauthorized_dialog

        show_unauthorized_dialog()
        st.stop()

    # Access control logic
    logged_in = st.session_state.logged_in

    # Ensure user role is resolved before building navigation tree if logged in
    if logged_in and "user_role" not in st.session_state and "user_teams" in st.session_state:
        from src.services.security_manager import SecurityManager

        st.session_state["user_role"] = SecurityManager.get_user_role(st.session_state["user_teams"])

    user_role = st.session_state.get("user_role")
    logger.debug("Building navigation tree (logged_in=%s, user_role=%s)", logged_in, user_role)
    nav_tree = NavigationService.get_navigation_tree(logged_in, user_role)

    pg = st.navigation(nav_tree)

    if not logged_in:
        hide_sidebar_nav()

    # 4. Handle Redirection
    NavigationService.handle_redirection(pg)

    # Run the selected page
    logger.debug("Running page: %s", getattr(pg, "title", pg))
    try:
        pg.run()
    except Exception as e:
        from src.frontend.ui_utils import handle_ui_error

        mastodon_url = st.secrets.get("contact", {}).get("mastodon_url")
        contact = f" Please report this issue on Mastodon: {mastodon_url}" if mastodon_url else ""
        handle_ui_error(e, f"An unexpected error occurred.{contact}", logger_name="snea.app")


if __name__ == "__main__":
    main()
