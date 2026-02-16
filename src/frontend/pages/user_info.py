# Copyright (c) 2026 Brothertown Language
# <!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->

import streamlit as st

def user_info_page() -> None:
    from src.services.identity_service import IdentityService
    from src.frontend.ui_utils import apply_standard_layout_css
    apply_standard_layout_css()
    
    if not st.session_state.get("logged_in"):
        st.warning("Please login to view user information.")
        if st.button("Go to Login"):
            from src.services.navigation_service import NavigationService
            st.switch_page(NavigationService.PAGE_LOGIN)
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
            "Email": st.session_state.get("user_email") or user.get("email"),
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
        identity_data = IdentityService.get_user_teams_and_orgs()
        
        st.divider()
        st.markdown("### Organizations")
        for org in identity_data["organizations"]:
            st.write(f"- {org}")

    if "user_teams" in st.session_state and st.session_state["user_teams"]:
        identity_data = IdentityService.get_user_teams_and_orgs()
        
        st.divider()
        st.markdown("### Teams")
        # Display team names from original session state but using identity_data as a sanity check
        for team in st.session_state["user_teams"]:
            st.write(f"- {team.get('name')} ({team.get('organization', {}).get('login')})")
        
        # Display team slugs from IdentityService (D.R.Y. demonstration)
        with st.expander("Team Slugs (extracted via IdentityService)"):
            for slug in identity_data["teams"]:
                st.write(f"- {slug}")

    # Removed "Raw User Data" expander as per instructions

if __name__ == "__main__":
    user_info_page()
