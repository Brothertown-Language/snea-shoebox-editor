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

    # Trigger secrets check and database readiness early
    try:
        ensure_secrets_present()
        ensure_db_alive()
        get_db_url()
    except Exception:
        pass

    # Initialize session state for authentication
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    # Define pages
    # Note: We use lazy initialization in page files (importing streamlit inside the function)
    # as the default approach to ensure they are only loaded when called.
    page_login = st.Page("pages/login.py", title="Login", icon="🔐", url_path="login")
    page_status = st.Page("pages/system_status.py", title="System Status", icon="📊", url_path="status", default=True)
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
        # Multipage navigation definition
        # Note: We use file paths (e.g., "pages/index.py") for st.Page to ensure
        # compatibility with st.switch_page() calls in subpages.
        pg = st.navigation({
            "Main": [page_home, page_record, page_source],
            "System": [page_status],
            "Account": [page_user, st.Page(logout, title="Logout", icon="🚪")]
        })
    else:
        pg = st.navigation([page_login])

    # Run the selected page
    pg.run()

def logout():
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
