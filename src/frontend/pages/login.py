# Copyright (c) 2026 Brothertown Language
import streamlit as st

@st.dialog("Access Restricted")
def show_unauthorized_dialog() -> None:
    """Display a non-closable dialog for unauthorized users."""
    # Hide the close button [x] using CSS
    st.html(
        """
        <style>
        button[aria-label="Close"] {
            display: none;
        }
        </style>
        """
    )
    st.error("Restricted Access")
    st.write(
        "This application is reserved for linguists and technicians "
        "collaborating on the proto-Southern New England Algonquian reconstruction "
        "project for the purpose of future Brothertown Language reconstruction."
    )
    mastodon_url = st.secrets.get("contact", {}).get("mastodon_url")
    if mastodon_url:
        st.write(
            f"For technical assistance or access requests, please contact "
            f"Michael Conrad on Mastodon: [{mastodon_url}]({mastodon_url})"
        )

    if st.button("Reload App"):
        # Clear session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        
        from src.frontend.ui_utils import reload_page_at_root
        reload_page_at_root(delay_ms=100)
        st.stop()

def login():
    import streamlit as st
    from streamlit_oauth import OAuth2Component
    import requests

    print("DEBUG: Login page loaded", flush=True)

    if "cookie_controller" not in st.session_state:
        # Fallback in case app.py didn't set it (shouldn't happen with updated app.py)
        from streamlit_cookies_controller import CookieController
        st.session_state["cookie_controller"] = CookieController()

    controller = st.session_state["cookie_controller"]

    # Initialize OAuth2Component safely
    try:
        oauth2 = OAuth2Component(
            st.secrets["github_oauth"]["client_id"],
            st.secrets["github_oauth"]["client_secret"],
            st.secrets["github_oauth"]["authorize_url"],
            st.secrets["github_oauth"]["token_url"],
            st.secrets["github_oauth"]["redirect_uri"]
        )
    except Exception as e:
        st.error(f"Failed to initialize OAuth component: {e}")
        print(f"ERROR: OAuth2Component initialization failed: {e}")
        st.stop()

    if st.session_state.get("is_unauthorized"):
        show_unauthorized_dialog()
        st.stop()

    if st.session_state.get("logged_in") and "auth" in st.session_state:
        from src.services.identity_service import IdentityService
        if IdentityService.is_identity_synchronized():
            # If there's a redirected page in query params, go there, otherwise home
            if "next" in st.query_params:
                next_page = st.query_params.pop("next")
                if "logout" in next_page:
                    st.switch_page("pages/index.py")
                else:
                    st.switch_page(next_page)
            else:
                st.switch_page("pages/index.py")
            return

    if "auth" not in st.session_state:
        try:
            result = oauth2.authorize_button(
                name="Continue with GitHub",
                redirect_uri=st.secrets["github_oauth"]["redirect_uri"],
                scope="read:user user:email read:org",
            )
        except Exception as e:
            st.error(f"OAuth authorization failed: {e}")
            print(f"ERROR: OAuth authorize_button failed: {e}")
            st.stop()
            
        if result:
            st.session_state["auth"] = result
            st.session_state.logged_in = True
            
            # PERSIST: Store the result in a browser cookie
            from src.frontend.constants import GH_AUTH_TOKEN_COOKIE
            controller.set(GH_AUTH_TOKEN_COOKIE, result)

            st.success("Login successful! Setting session...")
            import time
            time.sleep(1)  # Give the component a moment to set the cookie
            st.rerun()

    # If we have auth, ensure user identity (profile, teams, orgs) is fully synchronized.
    # CRITICAL: Logic now resides in app.py for global coverage and to prevent 
    # race conditions during redirection. We keep this check here as a 
    # secondary fallback to ensure a smooth transition during the login rerun.
    if "auth" in st.session_state:
        from src.services.identity_service import IdentityService
        from src.frontend.constants import GH_AUTH_TOKEN_COOKIE
        
        if IdentityService.is_identity_synchronized():
            st.session_state.logged_in = True
            # If there's a redirected page in query params, go there, otherwise home
            if "next" in st.query_params:
                next_page = st.query_params.pop("next")
                if "logout" in next_page:
                    st.switch_page("pages/index.py")
                else:
                    st.switch_page(next_page)
            else:
                st.switch_page("pages/index.py")
        else:
            # Fetch user info immediately after obtaining the token
            token = st.session_state["auth"]["token"]["access_token"]
            
            if IdentityService.sync_identity(token):
                st.session_state.logged_in = True
                st.rerun()
            else:
                # If not authorized, the function sets st.session_state["is_unauthorized"]
                # we should also clear cookie
                if st.session_state.get("is_unauthorized"):
                    try:
                        if controller.get(GH_AUTH_TOKEN_COOKIE) is not None:
                            controller.remove(GH_AUTH_TOKEN_COOKIE)
                    except Exception:
                        pass
                st.rerun()

if __name__ == "__main__":
    login()
