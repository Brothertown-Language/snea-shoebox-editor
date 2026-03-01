# Copyright (c) 2026 Brothertown Language
# <!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
import streamlit as st
from src.logging_config import get_logger

logger = get_logger("snea.app")

# import src.frontend.pages as pages
from src.database import init_db, get_db_url
from src.frontend.ui_utils import hide_sidebar_nav

@st.cache_resource
def _initialize_database():
    """Run database initialization once on app startup.

    Retries with exponential back-off to handle transient failures
    (e.g., local PostgreSQL still shutting down). Shows a user-friendly
    spinner and guidance instead of flooding the UI/logs.
    """
    import time as _time
    import socket
    from urllib.parse import urlparse

    max_attempts = 60
    base_delay = 1.0  # seconds
    max_delay = 10.0  # seconds cap

    with st.spinner("Initializing database…"):
        status = st.empty()
        for attempt in range(1, max_attempts + 1):
            try:
                # 1. DNS Pre-connect check
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

                # 2. Schema initialization
                init_db()
                status.empty()
                return  # success
            except Exception as e:
                err_msg = str(e).lower()
                is_transient = any(phrase in err_msg for phrase in (
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
                ))
                
                # Fetch remote status if in production to enrich logs
                from src.database import is_production
                from src.services.infrastructure_service import InfrastructureService
                
                remote_info = ""
                if is_production():
                    config = InfrastructureService.get_aiven_config()
                    if config:
                        r_status = InfrastructureService.get_service_status(config)
                        remote_info = f" [remote_state={r_status or 'unknown'}]"
                        
                        # If POWEROFF, send start command to Aiven
                        if attempt == 1 and r_status == "POWEROFF":
                            logger.info("Aiven service is POWEROFF. Sending start command...")
                            InfrastructureService.start_service(config)
                            remote_info += " [start_sent]"
                
                if "dns resolution failed" in err_msg:
                    remote_info += " [dns=not_ready]"

                if is_transient and attempt < max_attempts:
                    delay = min(base_delay * attempt, max_delay)
                    # Log at WARNING as requested, including remote status
                    logger.warning(
                        "DB init transient failure %d/%d:%s %s — retrying in %.1fs",
                        attempt, max_attempts, remote_info, e, delay,
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
                    st.error(
                        "Database is unavailable. Please try one of the following:"
                    )
                    
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
    st.set_page_config(
        page_title="SNEA Shoebox Editor",
        page_icon="📚",
        layout="wide"
    )

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
                    # Generic error
                    st.error("Failed to fetch user information.")
    
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
    logger.debug("Running page: %s", getattr(pg, 'title', pg))
    pg.run()


if __name__ == "__main__":
    main()
