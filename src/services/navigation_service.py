# Copyright (c) 2026 Brothertown Language
import streamlit as st
from typing import Dict, List, Union

class NavigationService:
    """
    Service for managing application navigation and page registration.
    """

    # Central registry of pages
    # Paths are relative to src/frontend/
    PAGE_LOGIN = st.Page("pages/login.py", title="Login", icon="🔐", url_path="login")
    PAGE_STATUS = st.Page("pages/system_status.py", title="System Status", icon="📊", url_path="status")
    PAGE_HOME = st.Page("pages/index.py", title="Home", icon="🏠", url_path="index")
    PAGE_RECORD = st.Page("pages/view_record.py", title="Record View", icon="📝", url_path="record")
    PAGE_SOURCE = st.Page("pages/view_source.py", title="Source View", icon="📖", url_path="source")
    PAGE_USER = st.Page("pages/user_info.py", title="User Info", icon="👤", url_path="profile")
    PAGE_LOGOUT = st.Page("pages/logout.py", title="Logout", icon="🚪", url_path="logout")

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
            return {
                "Main": [cls.PAGE_HOME, cls.PAGE_RECORD, cls.PAGE_SOURCE],
                "System": [cls.PAGE_STATUS],
                "Account": [cls.PAGE_USER, cls.PAGE_LOGOUT]
            }
        else:
            # Include all pages in navigation even when not logged in,
            # so Streamlit doesn't fallback to the first page (/) and we can 
            # capture the intended destination.
            return [
                cls.PAGE_LOGIN, 
                cls.PAGE_HOME, 
                cls.PAGE_RECORD, 
                cls.PAGE_SOURCE, 
                cls.PAGE_STATUS, 
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
            cls.PAGE_RECORD: "pages/view_record.py",
            cls.PAGE_SOURCE: "pages/view_source.py",
            cls.PAGE_USER: "pages/user_info.py",
        }
