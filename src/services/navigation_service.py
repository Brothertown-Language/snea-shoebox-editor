# Copyright (c) 2026 Brothertown Language
# <!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
import streamlit as st
from typing import Dict, List, Union
from src.logging_config import get_logger

logger = get_logger("snea.navigation")

# Central registry of pages
# Paths are relative to src/frontend/
PAGE_LOGIN = st.Page("pages/login.py", title="Login", icon="🔐", url_path="login")
PAGE_STATUS = st.Page("pages/system_status.py", title="System Status", icon="📊", url_path="status")
PAGE_HOME = st.Page("pages/index.py", title="Home", icon="🏠", url_path="index", default=True)
PAGE_USER = st.Page("pages/user_info.py", title="User Info", icon="👤", url_path="profile")
PAGE_UPLOAD = st.Page("pages/upload_mdf.py", title="Upload MDF", icon="📤", url_path="upload")
PAGE_TABLE_MAINTENANCE = st.Page("pages/table_maintenance.py", title="Table Maintenance", icon="🛠️", url_path="maintenance")
PAGE_LOGOUT = st.Page("pages/logout.py", title="Logout", icon="🚪", url_path="logout")

class NavigationService:
    """
    Service for managing application navigation and page registration.
    """

    # Expose pages as class attributes for compatibility
    PAGE_LOGIN = PAGE_LOGIN
    PAGE_STATUS = PAGE_STATUS
    PAGE_HOME = PAGE_HOME
    PAGE_USER = PAGE_USER
    PAGE_UPLOAD = PAGE_UPLOAD
    PAGE_TABLE_MAINTENANCE = PAGE_TABLE_MAINTENANCE
    PAGE_LOGOUT = PAGE_LOGOUT

    @classmethod
    def get_navigation_tree(cls, logged_in: bool = False) -> Union[Dict[str, List[st.Page]], List[st.Page]]:
        """
        Returns the navigation structure based on login status and user role.
        
        Args:
            logged_in: Whether the user is currently logged in.
            
        Returns:
            A dictionary or list formatted for st.navigation.
        """
        if logged_in:
            logger.debug("Returning authenticated navigation tree")
            return {
                "Main": [cls.PAGE_HOME, cls.PAGE_UPLOAD],
                "System": [cls.PAGE_STATUS, cls.PAGE_TABLE_MAINTENANCE],
                "Account": [cls.PAGE_USER, cls.PAGE_LOGOUT]
            }
        else:
            logger.debug("Returning unauthenticated navigation tree")
            # Include all pages in navigation even when not logged in,
            # so Streamlit doesn't fallback to the first page (/) and we can 
            # capture the destination.
            return [
                cls.PAGE_LOGIN, 
                cls.PAGE_HOME, 
                cls.PAGE_UPLOAD,
                cls.PAGE_STATUS, 
                cls.PAGE_TABLE_MAINTENANCE,
                cls.PAGE_USER, 
                cls.PAGE_LOGOUT
            ]

    @classmethod
    def get_page_to_path_map(cls) -> Dict[st.Page, str]:
        """
        Returns a mapping of page objects to their script paths.
        Used for deep-link redirection logic.
        """
        return {
            cls.PAGE_STATUS: "pages/system_status.py",
            cls.PAGE_HOME: "pages/index.py",
            cls.PAGE_USER: "pages/user_info.py",
            cls.PAGE_UPLOAD: "pages/upload_mdf.py",
            cls.PAGE_TABLE_MAINTENANCE: "pages/table_maintenance.py",
        }

    @classmethod
    def handle_redirection(cls, pg: st.Page):
        """
        Centralizes deep-link and post-login redirection logic.
        
        Args:
            pg: The current page object returned by st.navigation().
        """
        logged_in = st.session_state.get("logged_in", False)
        
        # 1. Handle Unauthenticated Access (Deep Linking)
        if not logged_in and pg != cls.PAGE_LOGIN:
            if pg == cls.PAGE_LOGOUT:
                logger.debug("Unauthenticated user hit logout, redirecting to login")
                st.switch_page(cls.PAGE_LOGIN)
            
            page_to_path = cls.get_page_to_path_map()
            if pg in page_to_path:
                current_params = {k: v for k, v in st.query_params.items()}
                current_params["next"] = page_to_path[pg]
                st.session_state["redirect_params"] = current_params
                logger.debug("Deep-link captured, redirecting to login with next=%s", page_to_path[pg])
                st.switch_page(cls.PAGE_LOGIN)

        # 2. Global redirection handler after login/rehydration
        from src.services.identity_service import IdentityService
        from src.services.security_manager import SecurityManager
        
        if logged_in and IdentityService.is_identity_synchronized():
            # Ensure user role is set
            if "user_role" not in st.session_state:
                user_teams = st.session_state.get("user_teams", [])
                st.session_state["user_role"] = SecurityManager.get_user_role(user_teams)
            
            # Priority 1: Check session state for saved params (from deep links)
            if "redirect_params" in st.session_state:
                params = st.session_state.pop("redirect_params")
                next_page = params.pop("next", "pages/index.py")
                logger.debug("Post-login redirect to deep-link: %s", next_page)
                for k, v in params.items():
                    st.query_params[k] = v
                st.switch_page(next_page)
                
            # Priority 2: Check query params (simple internal redirects)
            elif "next" in st.query_params:
                next_page = st.query_params["next"]
                logger.debug("Post-login redirect via query param: %s", next_page)
                del st.query_params["next"]
                
                # If next points to logout, ignore it to prevent immediate logout after login
                if "logout.py" in next_page or "logout" in next_page:
                    st.switch_page("pages/index.py")
                else:
                    st.switch_page(next_page)
