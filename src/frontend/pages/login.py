# Copyright (c) 2026 Brothertown Language
"""
AI Coding Defaults:
- Strict Typing: Mandatory for all function signatures and variable declarations.
- Lazy Initialization: Imports inside functions for Streamlit pages to optimize loading.
- Single Responsibility: Each function/method must have one clear purpose.
- Standalone Execution: Page files must include a main execution block.
- Background Execution: MANDATORY use of nohup for all Streamlit runs (e.g. scripts/start_streamlit.sh).
"""
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
                st.session_state["user_teams"] = teams_response.json()
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
