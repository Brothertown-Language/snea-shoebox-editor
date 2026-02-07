# Copyright (c) 2026 Brothertown Language
"""
AI Coding Defaults:
- Strict Typing: Mandatory for all function signatures and variable declarations.
- Lazy Initialization: Imports inside functions for Streamlit pages to optimize loading.
- Single Responsibility: Each function/method must have one clear purpose.
- Standalone Execution: Page files must include a main execution block.
- Background Execution: MANDATORY use of nohup for all Streamlit runs (e.g. scripts/start_streamlit.sh).
- Local Development: MANDATORY use of "uv run --extra local" to ensure pgserver is available.
"""
import streamlit as st

def logout_page() -> None:
    """
    Handle the logout process: clear session, purge cookies, 
    and redirect to root with a full browser reload.
    """
    print("DEBUG: Logout page entered", flush=True)
    
    from src.frontend.constants import GH_AUTH_TOKEN_COOKIE
    from src.frontend.ui_utils import reload_page_at_root
    
    # 1. Purge the cookie safely
    if "cookie_controller" in st.session_state:
        controller = st.session_state["cookie_controller"]
        try:
            if controller.get(GH_AUTH_TOKEN_COOKIE) is not None:
                controller.remove(GH_AUTH_TOKEN_COOKIE)
        except Exception:
            pass

    # 2. Clear all session state
    for key in list(st.session_state.keys()):
        # Preserve cookie_controller if needed, but usually a full reload handles it.
        # Actually, let's clear everything as we're doing a full reload.
        del st.session_state[key]
        
    st.session_state.logged_in = False
    
    st.info("Logged out successfully! Redirecting...")
    
    # 3. Reload at root
    # The user says: "in that page [logout.py], have it use streamlit navigation 
    # to change to / and run the reload code after doing that"
    
    # We set a flag and switch to index.py. In index.py, we will check this flag
    # and trigger the full browser reload to root (/).
    st.session_state.trigger_logout_reload = True
    st.switch_page("pages/index.py")

if __name__ == "__main__":
    logout_page()
