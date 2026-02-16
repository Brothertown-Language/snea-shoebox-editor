# Copyright (c) 2026 Brothertown Language
# <!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
import streamlit as st

def logout_page() -> None:
    """
    Handle the logout process: clear session, purge cookies, 
    and redirect to root with a full browser reload.
    """
    from src.logging_config import get_logger
    logger = get_logger("snea.logout")
    from src.frontend.ui_utils import apply_standard_layout_css
    apply_standard_layout_css()
    logger.debug("Logout page entered")
    
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
    from src.services.navigation_service import NavigationService
    st.switch_page(NavigationService.PAGE_HOME)

if __name__ == "__main__":
    logout_page()
