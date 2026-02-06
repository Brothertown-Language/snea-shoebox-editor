# Copyright (c) 2026 Brothertown Language
"""
Authentication utilities for GitHub OAuth.
"""
import streamlit as st
import requests
from typing import Optional, Dict, Any, List

def fetch_github_user_info(access_token: str) -> bool:
    """
    Fetch user info, organizations, and teams from GitHub and store in session state.
    Returns True if successful and authorized, False otherwise.
    """
    headers = {
        "Authorization": f"token {access_token}",
        "Accept": "application/json"
    }
    base_url = st.secrets["github_oauth"]["user_info_url"]

    try:
        # Fetch user profile
        user_response = requests.get(base_url, headers=headers)
        user_response.raise_for_status()
        st.session_state["user_info"] = user_response.json()

        # Fetch organizations
        orgs_response = requests.get(f"{base_url}/orgs", headers=headers)
        orgs_response.raise_for_status()
        st.session_state["user_orgs"] = orgs_response.json()

        # Fetch teams
        teams_response = requests.get(f"{base_url}/teams", headers=headers)
        teams_response.raise_for_status()
        user_teams = teams_response.json()
        st.session_state["user_teams"] = user_teams

        # Verify team membership
        # Must be in Brothertown-Language / proto-SNEA
        is_authorized = False
        for team in user_teams:
            team_name = team.get("name")
            org_info = team.get("organization", {})
            org_login = org_info.get("login")

            if team_name == "proto-SNEA" and org_login == "Brothertown-Language":
                is_authorized = True
                break

        if not is_authorized:
            st.session_state["is_unauthorized"] = True
            return False

        return True

    except Exception as e:
        st.error(f"Failed to fetch user information from GitHub: {e}")
        return False
