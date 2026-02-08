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
    # We check if 'auth' is missing from session but present in cookies
    from src.frontend.constants import GH_AUTH_TOKEN_COOKIE
    saved_token = controller.get(GH_AUTH_TOKEN_COOKIE)
    if saved_token and "auth" not in st.session_state:
        print("DEBUG: Rehydrating session from cookie", flush=True)
        st.session_state["auth"] = saved_token
        st.session_state.logged_in = True
    
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
    
    # Define pages
    page_login = st.Page("pages/login.py", title="Login", icon="🔐", url_path="login")
    page_status = st.Page("pages/system_status.py", title="System Status", icon="📊", url_path="status")
    page_home = st.Page("pages/index.py", title="Home", icon="🏠", url_path="index")
    page_record = st.Page("pages/view_record.py", title="Record View", icon="📝", url_path="record")
    page_source = st.Page("pages/view_source.py", title="Source View", icon="📖", url_path="source")
    page_user = st.Page("pages/user_info.py", title="User Info", icon="👤", url_path="profile")
    page_logout = st.Page("pages/logout.py", title="Logout", icon="🚪", url_path="logout")

    if st.session_state.get("is_unauthorized"):
        from src.frontend.pages.login import show_unauthorized_dialog
        show_unauthorized_dialog()
        st.stop()

    # Access control logic
    if st.session_state.logged_in:
        pg = st.navigation({
            "Main": [page_home, page_record, page_source],
            "System": [page_status],
            "Account": [page_user, page_logout]
        })
    else:
        # Include all pages in navigation even when not logged in,
        # so Streamlit doesn't fallback to the first page (/) and we can 
        # capture the intended destination.
        pg = st.navigation([page_login, page_home, page_record, page_source, page_status, page_user, page_logout])
        
        # Hide the sidebar navigation links when not logged in
        st.markdown(
            """
            <style>
            [data-testid="stSidebarNav"] {
                display: none;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

    # Run the selected page
    if not st.session_state.logged_in and pg != page_login:
        # If we just landed on a deep link, save it and redirect to login
        current_params = {k: v for k, v in st.query_params.items()}
        
        # Map page objects to their script paths
        page_to_path = {
            page_status: "pages/system_status.py",
            page_home: "pages/index.py",
            page_record: "pages/view_record.py",
            page_source: "pages/view_source.py",
            page_user: "pages/user_info.py",
        }
        
        if pg in page_to_path:
            current_params["next"] = page_to_path[pg]
            # Store in session state for persistence across OAuth redirect
            st.session_state["redirect_params"] = current_params
            st.switch_page(page_login)
        elif pg == page_logout:
            # If they hit logout while not logged in, just go to login
            st.switch_page(page_login)
    
    # Global redirection handler after login/rehydration
    # CRITICAL: Do not redirect to the home page until ALL identity data (profile, 
    # orgs, teams) is fully loaded and synchronized with the database.
    # This prevents the app from landing on the home page with missing profile or org/team data.
    from src.frontend.auth_utils import is_identity_synchronized
    if st.session_state.logged_in and is_identity_synchronized():
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
