# Copyright (c) 2026 Brothertown Language
import streamlit as st
import sys
import os

# Add the project root to sys.path to ensure src imports work
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import src.frontend.pages as pages
from src.database import get_db_url, init_db
from src.aiven_utils import ensure_db_alive, ensure_secrets_present
@st.cache_resource
def _initialize_database():
    """Run database initialization once on app startup."""
    try:
        init_db()
    except Exception as e:
        st.error(f"Critical Error: Failed to initialize database: {e}")
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
    SecurityManager.rehydrate_session()
    
    # 3. Global Identity Synchronization
    # CRITICAL: This logic must remain in app.py to prevent race conditions.
    # By fetching user info (including profile, orgs, and teams) here, we ensure 
    # it's available regardless of which page the user lands on first after 
    # OAuth or cookie rehydration.
    if "auth" in st.session_state:
        from src.services.identity_service import IdentityService
        access_token = st.session_state["auth"].get("token", {}).get("access_token")
        if access_token:
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
    nav_tree = NavigationService.get_navigation_tree(logged_in)
    
    pg = st.navigation(nav_tree)

    if not logged_in:
        # Hide the sidebar navigation links when not logged in
        st.html(
            """
            <style>
            [data-testid="stSidebarNav"] {
                display: none;
            }
            </style>
            """
        )

    # 4. Handle Redirection
    NavigationService.handle_redirection(pg)
    
    # Run the selected page
    pg.run()


if __name__ == "__main__":
    main()
