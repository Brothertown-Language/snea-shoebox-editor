# Copyright (c) 2026 Brothertown Language
"""
AI Coding Defaults:
- Strict Typing: Mandatory for all function signatures and variable declarations.
- Lazy Initialization: Imports inside functions for Streamlit pages to optimize loading.
- Single Responsibility: Each function/method must have one clear purpose.
- Standalone Execution: Page files must include a main execution block.
- Background Execution: MANDATORY use of nohup for all Streamlit runs (e.g. scripts/start_streamlit.sh).
"""
import streamlit as st
import sys
import os

# Add the project root to sys.path to ensure src imports work
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import src.frontend.pages as pages
from src.database import get_db_url
from src.aiven_utils import ensure_db_alive, ensure_secrets_present


def main():
    # Page configuration MUST be the first Streamlit command
    st.set_page_config(
        page_title="SNEA Shoebox Editor",
        page_icon="📚",
        layout="wide"
    )

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
    saved_token = controller.get("gh_auth_token")
    if saved_token and "auth" not in st.session_state:
        st.session_state["auth"] = saved_token
        st.session_state.logged_in = True
        
        # Re-fetch user info if missing
        if "user_info" not in st.session_state:
            from src.frontend.auth_utils import fetch_github_user_info
            access_token = saved_token.get("token", {}).get("access_token")
            if access_token:
                fetch_github_user_info(access_token)
        # No rerun here; let it fall through to navigation with updated state

    # Define pages
    page_login = st.Page("pages/login.py", title="Login", icon="🔐", url_path="login")
    page_status = st.Page("pages/system_status.py", title="System Status", icon="📊", url_path="status")
    page_home = st.Page("pages/index.py", title="Home", icon="🏠", url_path="index")
    page_record = st.Page("pages/view_record.py", title="Record View", icon="📝", url_path="record")
    page_source = st.Page("pages/view_source.py", title="Source View", icon="📖", url_path="source")
    page_user = st.Page("pages/user_info.py", title="User Info", icon="👤", url_path="profile")

    if st.session_state.get("is_unauthorized"):
        from src.frontend.pages.login import show_unauthorized_dialog
        show_unauthorized_dialog()
        st.stop()

    # Access control logic
    if st.session_state.logged_in:
        pg = st.navigation({
            "Main": [page_home, page_record, page_source],
            "System": [page_status],
            "Account": [page_user, st.Page(logout, title="Logout", icon="🚪")]
        })
    else:
        # Include all pages in navigation even when not logged in,
        # so Streamlit doesn't fallback to the first page (/) and we can 
        # capture the intended destination.
        pg = st.navigation([page_login, page_home, page_record, page_source, page_status, page_user])
        
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
    
    # Global redirection handler after login/rehydration
    if st.session_state.logged_in:
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
            st.switch_page(next_page)

    pg.run()


def logout():
    # Purge the cookie safely
    if "cookie_controller" in st.session_state:
        controller = st.session_state["cookie_controller"]
        try:
            # Check if cookie exists before removing to avoid KeyError
            if controller.get("gh_auth_token") is not None:
                controller.remove("gh_auth_token")
        except Exception:
            # Best effort removal
            pass

    st.session_state.logged_in = False
    if "auth" in st.session_state:
        del st.session_state["auth"]
    if "user_info" in st.session_state:
        del st.session_state["user_info"]
    if "user_orgs" in st.session_state:
        del st.session_state["user_orgs"]
    if "user_teams" in st.session_state:
        del st.session_state["user_teams"]
    st.info("Logged out successfully!")
    st.rerun()


if __name__ == "__main__":
    main()
