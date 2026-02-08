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

    # Run the selected page
    if not logged_in and pg != NavigationService.PAGE_LOGIN:
        # If we just landed on a deep link, save it and redirect to login
        current_params = {k: v for k, v in st.query_params.items()}
        
        # Map page objects to their script paths
        page_to_path = NavigationService.get_page_to_path_map()
        
        if pg in page_to_path:
            current_params["next"] = page_to_path[pg]
            # Store in session state for persistence across OAuth redirect
            st.session_state["redirect_params"] = current_params
            st.switch_page(NavigationService.PAGE_LOGIN)
        elif pg == NavigationService.PAGE_LOGOUT:
            # If they hit logout while not logged in, just go to login
            st.switch_page(NavigationService.PAGE_LOGIN)
    
    # Global redirection handler after login/rehydration
    # CRITICAL: Do not redirect to the home page until ALL identity data (profile, 
    # orgs, teams) is fully loaded and synchronized with the database.
    # This prevents the app from landing on the home page with missing profile or org/team data.
    from src.frontend.auth_utils import is_identity_synchronized
    if st.session_state.logged_in and is_identity_synchronized():
        # Get user role for redirection and permission logic
        user_teams = st.session_state.get("user_teams", [])
        st.session_state["user_role"] = SecurityManager.get_user_role(user_teams)
        
        # Priority 1: Check session state for saved params (from deep links)
        if "redirect_params" in st.session_state:
            params = st.session_state.pop("redirect_params")
            next_page = params.pop("next", "pages/index.py")
            for k, v in params.items():
                st.query_params[k] = v
            st.switch_page(next_page)
            
        # Priority 2: Check query params (simple internal redirects)
        elif "next" in st.query_params:
            next_page = st.query_params["next"]
            del st.query_params["next"]
            
            # If next points to logout, ignore it to prevent immediate logout after login
            if "logout.py" in next_page or "logout" in next_page:
                st.switch_page("pages/index.py")
            else:
                st.switch_page(next_page)

    pg.run()


if __name__ == "__main__":
    main()
