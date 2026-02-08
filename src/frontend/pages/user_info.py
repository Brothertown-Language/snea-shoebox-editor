# Copyright (c) 2026 Brothertown Language
"""
AI Coding Defaults:
- **ANTI-"VIBE" CODING:** This is NOT a "VIBE" coding project. Avoid "VIBE" coding with prejudice.
- **Human Review:** ALL code changes MUST be reviewed by the Human Lead.
- Strict Typing: Mandatory for all function signatures and variable declarations.
- Lazy Initialization: Imports inside functions for Streamlit pages to optimize loading.
- Single Responsibility: Each function/method must have one clear purpose.
- Standalone Execution: Page files must include a main execution block.
- Background Execution: MANDATORY use of nohup for all Streamlit runs (e.g. scripts/start_streamlit.sh).
- Local Development: MANDATORY use of "uv run --extra local" to ensure pgserver is available.
"""

def user_info_page() -> None:
    import streamlit as st
    
    st.title("User Information")
    
    if not st.session_state.get("logged_in"):
        st.warning("Please login to view user information.")
        if st.button("Go to Login"):
            st.switch_page("pages/login.py")
        return

    user = st.session_state.get("user_info")
    
    if user:
        # Debugging aid (always available for now while troubleshooting)
        with st.expander("Session Debug Info"):
            st.write("Logged In:", st.session_state.get("logged_in"))
            st.write("User object keys:", list(user.keys()))
            if st.button("Force Rerun"):
                st.rerun()
            if st.button("Clear Session & Logout"):
                # Clear all session state
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                
                from src.frontend.ui_utils import reload_page_at_root
                reload_page_at_root(delay_ms=100)
                st.stop()

        col1, col2 = st.columns([1, 3])
        
        with col1:
            if "avatar_url" in user:
                st.image(user["avatar_url"], width=150)
        
        with col2:
            st.subheader(user.get("name", user.get("login", "Unknown User")))
            st.text(f"Username: {user.get('login')}")
            if user.get("bio"):
                st.info(user.get("bio"))
                
        st.divider()
        
        st.markdown("### GitHub Profile Details")
        details = {
            "Email": user.get("email"),
            "Location": user.get("location"),
            "Company": user.get("company"),
            "Public Repos": user.get("public_repos"),
            "Followers": user.get("followers"),
            "Following": user.get("following"),
            "GitHub URL": user.get("html_url")
        }
        
        for label, value in details.items():
            if value is not None:
                st.write(f"**{label}:** {value}")
    else:
        st.warning("No profile information available.")

    if "user_orgs" in st.session_state and st.session_state["user_orgs"]:
        st.divider()
        st.markdown("### Organizations")
        for org in st.session_state["user_orgs"]:
            st.write(f"- {org.get('login')}")

    if "user_teams" in st.session_state and st.session_state["user_teams"]:
        st.divider()
        st.markdown("### Teams")
        for team in st.session_state["user_teams"]:
            st.write(f"- {team.get('name')} ({team.get('organization', {}).get('login')})")

    # Removed "Raw User Data" expander as per instructions

if __name__ == "__main__":
    user_info_page()
