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

@st.dialog("Access Restricted", clear_on_submit=False)
def show_unauthorized_dialog() -> None:
    """Display a non-closable dialog for unauthorized users."""
    st.error("Restricted Access")
    st.write(
        "This application is reserved for linguists and technicians "
        "collaborating on the Southern New England Algonquian reconstruction "
        "project for the purpose of future Brothertown Language reconstruction."
    )
    st.write(
        "For technical assistance or access requests, please contact "
        "Michael Conrad on Mastodon: [https://mastodon.social/@michaelconrad](https://mastodon.social/@michaelconrad)"
    )
    
    if st.button("Reload App"):
        # Clear session state and rerun
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

def login():
    import streamlit as st
    
    from streamlit_oauth import OAuth2Component
    import requests

    # Initialize OAuth2Component
    oauth2 = OAuth2Component(
        st.secrets["github_oauth"]["client_id"],
        st.secrets["github_oauth"]["client_secret"],
        st.secrets["github_oauth"]["authorize_url"],
        st.secrets["github_oauth"]["token_url"],
        st.secrets["github_oauth"]["redirect_uri"],
        None
    )

    if st.session_state.get("is_unauthorized"):
        show_unauthorized_dialog()
        st.stop()

    if st.session_state.get("logged_in") and "auth" in st.session_state:
        st.switch_page("pages/index.py")
        return

    if "auth" not in st.session_state:
        result = oauth2.authorize_button(
            name="Continue with GitHub",
            redirect_uri=st.secrets["github_oauth"]["redirect_uri"],
            scope="read:user user:email read:org",
        )
        if result:
            # Save token to session state
            st.session_state["auth"] = result
            
            # Fetch user info immediately after obtaining the token
            token = result["token"]["access_token"]
            headers = {
                "Authorization": f"token {token}",
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
                    st.rerun()

            except Exception as e:
                st.error(f"Failed to fetch user information from GitHub: {e}")
            
            st.session_state.logged_in = True
            st.rerun()
    else:
        # If already has auth but not redirected yet
        st.success("Successfully logged in!")
        st.switch_page("pages/index.py")

if __name__ == "__main__":
    login()
