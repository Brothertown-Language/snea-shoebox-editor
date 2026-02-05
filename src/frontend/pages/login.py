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

    # Retrieve OAuth configuration from secrets.toml
    # By default, OAuth2Component looks for a section named "oauth" in st.secrets if no config is passed
    # Create OAuth2Component instance
    oauth2 = OAuth2Component(
        st.secrets["github_oauth"]["client_id"],
        st.secrets["github_oauth"]["client_secret"],
        st.secrets["github_oauth"]["authorize_url"],
        st.secrets["github_oauth"]["token_url"],
        st.secrets["github_oauth"]["redirect_uri"],
        None # scope is handled in the button
    )

    if "auth" not in st.session_state:
        result = oauth2.authorize_button(
            name="Continue with GitHub",
            redirect_uri=st.secrets["github_oauth"]["redirect_uri"],
            scope="read:user user:email read:org",
        )
        if result:
            # Save token to session state
            st.session_state["auth"] = result
            st.rerun()
    else:
        # Retrieve the access token
        token = st.session_state["auth"]["token"]["access_token"]

        # 4. Fetch the user's Organizations and Teams using the token
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/json"
        }

        base_url = st.secrets["github_oauth"]["user_info_url"]
        orgs_url = f"{base_url}/orgs"
        teams_url = f"{base_url}/teams"

        orgs_response = requests.get(orgs_url, headers=headers)
        orgs_data = orgs_response.json()

        teams_response = requests.get(teams_url, headers=headers)
        teams_data = teams_response.json()

        # 5. Display the Results
        st.success("Successfully logged in!")

        st.write("### Your Organizations (Groups)")
        if isinstance(orgs_data, list) and orgs_data:
            for org in orgs_data:
                st.write(f"- {org.get('login')}")
        else:
            st.info("No organizations found (or access was not granted).")

        st.write("### Your Teams")
        if isinstance(teams_data, list) and teams_data:
            for team in teams_data:
                team_name = team.get('name')
                org_info = team.get('organization')
                org_name = org_info.get('login') if org_info else 'Unknown Org'
                st.write(f"- {team_name} ({org_name})")
        else:
            st.info("No teams found (or access was not granted).")

        if st.button("Log out"):
            del st.session_state["auth"]
            st.rerun()

if __name__ == "__main__":
    login()
