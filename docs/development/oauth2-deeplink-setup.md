<!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
# OAuth2 and Deep Link Setup Guide

---
**Attribution**: This guide was generated with the assistance of an AI agent (Junie) as part of the SNEA Online Shoebox Editor development process.
---

This document provides step-by-step instructions for implementing a robust GitHub OAuth2 authentication system with deep linking and session persistence (via cookies) in a Streamlit application. 

The approach described here is directly taken from the implementation in the **SNEA Online Shoebox Editor** and has been made generic for use in other projects.

## 1. GitHub OAuth App Registration

First, register your application on GitHub:

1.  Go to **Settings** > **Developer settings** > **OAuth Apps** > **New OAuth App**.
2.  **Homepage URL**:
    *   Local: `http://localhost:8501`
    *   Production: `https://your-app.streamlit.app`
3.  **Authorization callback URL**:
    *   This MUST match the `redirect_uri` in your code.
    *   If using `streamlit-oauth`, it usually follows this pattern: `[HOMEPAGE_URL]/component/streamlit_oauth.authorize_button`
    *   Example Local: `http://localhost:8501/component/streamlit_oauth.authorize_button`
    *   Example Production: `https://your-app.streamlit.app/component/streamlit_oauth.authorize_button`

> [!TIP]
> It is MANDATORY to create **two separate** GitHub OAuth Apps: one for local development and one for production on Streamlit Community Cloud. This prevents redirect URI conflicts.

## 2. Project Dependencies

You will need the following Python packages:

```toml
# pyproject.toml or requirements.txt
streamlit-oauth = ">=0.1.11"
streamlit-cookies-controller = ">=0.0.4"
requests = ">=2.31.0"
```

## 3. Configuration (Secrets)

### Local Development
Store your local OAuth credentials in `.streamlit/secrets.toml`:

> [!DANGER]
> **NEVER commit your `.streamlit/secrets.toml` file to Git.**
> Ensure that `.streamlit/` is added to your `.gitignore` file. Committing secrets to a public (or even private) repository exposes your application to unauthorized access and security breaches. If you accidentally commit a secret, you MUST rotate it immediately.

```toml
[github_oauth]
client_id = "YOUR_LOCAL_CLIENT_ID"
client_secret = "YOUR_LOCAL_CLIENT_SECRET"
authorize_url = "https://github.com/login/oauth/authorize"
token_url = "https://github.com/login/oauth/access_token"
user_info_url = "https://api.github.com/user"
redirect_uri = "http://localhost:8501/component/streamlit_oauth.authorize_button"
```

### Production (Streamlit Community Cloud)
When deploying to **Streamlit Community Cloud**, do NOT use the local `secrets.toml` file. Instead, use the **Secrets** management UI in the Streamlit Cloud dashboard:

1.  Open your app settings on Streamlit Cloud.
2.  Go to the **Secrets** section.
3.  Paste your production credentials (using the production `redirect_uri` and GitHub App details):

```toml
[github_oauth]
client_id = "YOUR_PRODUCTION_CLIENT_ID"
client_secret = "YOUR_PRODUCTION_CLIENT_SECRET"
authorize_url = "https://github.com/login/oauth/authorize"
token_url = "https://github.com/login/oauth/access_token"
user_info_url = "https://api.github.com/user"
redirect_uri = "https://your-app.streamlit.app/component/streamlit_oauth.authorize_button"
```

> [!IMPORTANT]
> Always ensure the `redirect_uri` in your production secrets matches the one registered in your production GitHub OAuth App.

## 4. Implementation Strategy

The system relies on three main components:
1.  **Deep Link Capture**: Intercepting the requested URL before redirecting to login.
2.  **Cookie-based Persistence**: Storing the OAuth token in a browser cookie so users don't have to log in on every refresh.
3.  **Post-Login Redirection**: Returning the user to their originally requested page after successful authentication.
4.  **Identity Synchronization**: Ensuring user info, organizations, and teams are fully loaded and verified before allowing access to protected pages.
5.  **Database Integration**: Automatically syncing the GitHub user profile to the local `users` table upon successful login.

### A. Main Entry Point (`streamlit_app.py`)

The main file handles session rehydration and routing.

```python
import streamlit as st
from streamlit_cookies_controller import CookieController

def main():
    st.set_page_config(page_title="My App")

    # 1. Initialize Cookie Controller
    controller = CookieController()
    st.session_state["cookie_controller"] = controller

    # 2. Rehydrate Session from Cookie
    saved_token = controller.get("gh_auth_token")
    if saved_token and "auth" not in st.session_state:
        st.session_state["auth"] = saved_token
        st.session_state.logged_in = True

    # 3. Identity Synchronization (Wait for all data before routing)
    if "auth" in st.session_state:
        from src.frontend.auth_utils import fetch_github_user_info, is_identity_synchronized
        if not is_identity_synchronized():
            access_token = st.session_state["auth"].get("token", {}).get("access_token")
            if access_token:
                fetch_github_user_info(access_token)

    # 4. Define Pages
    page_login = st.Page("pages/login.py", title="Login", url_path="login")
    page_home = st.Page("pages/index.py", title="Home", url_path="index")
    # ... other pages

    # 4. Navigation & Access Control
    if st.session_state.get("logged_in"):
        pg = st.navigation([page_home, ...])
    else:
        # Include all pages so we can capture the deep link target
        pg = st.navigation([page_login, page_home, ...])

    # 5. Deep Link Handling
    if not st.session_state.get("logged_in") and pg != page_login:
        # Capture current page and query params
        current_params = {k: v for k, v in st.query_params.items()}
        # Map page object to script path for st.switch_page
        page_to_path = {page_home: "pages/index.py", ...}
        
        if pg in page_to_path:
            current_params["next"] = page_to_path[pg]
            st.session_state["redirect_params"] = current_params
            st.switch_page(page_login)

    # 6. Global Redirection after login
    if st.session_state.get("logged_in") and "redirect_params" in st.session_state:
        params = st.session_state.pop("redirect_params")
        next_page = params.pop("next", "pages/index.py")
        for k, v in params.items():
            st.query_params[k] = v
        st.switch_page(next_page)

    pg.run()
```

### B. Login Page (`pages/login.py`)

Handles the OAuth handshake and cookie storage.

```python
import streamlit as st
from streamlit_oauth import OAuth2Component

def login():
    controller = st.session_state["cookie_controller"]
    oauth2 = OAuth2Component(
        st.secrets["github_oauth"]["client_id"],
        st.secrets["github_oauth"]["client_secret"],
        st.secrets["github_oauth"]["authorize_url"],
        st.secrets["github_oauth"]["token_url"],
        st.secrets["github_oauth"]["redirect_uri"]
    )

    if not st.session_state.get("auth"):
        result = oauth2.authorize_button(
            name="Continue with GitHub",
            redirect_uri=st.secrets["github_oauth"]["redirect_uri"],
            scope="read:user",
        )
        if result:
            st.session_state["auth"] = result
            st.session_state.logged_in = True
            
            # Store in cookie for persistence
            controller.set("gh_auth_token", result)
            st.rerun()
    else:
        st.switch_page("pages/index.py")

if __name__ == "__main__":
    login()
```

## 5. User Authorization & Team Verification

The application can be restricted to specific GitHub Organizations or Teams. In the SNEA Editor, users must be members of the `proto-SNEA` team within the `Brothertown-Language` organization.

```python
def verify_user_authorization(user_teams):
    for team in user_teams:
        if (team.get("name") == "proto-SNEA" and 
            team.get("organization", {}).get("login") == "Brothertown-Language"):
            return True
    return False
```

## 6. Key Considerations

1.  **Strict Redirect URIs**: GitHub requires the `redirect_uri` to match EXACTLY what is registered in the GitHub App settings.
2.  **Cookie Security**: `streamlit-cookies-controller` manages browser cookies. Ensure your application handles sensitive tokens securely.
3.  **Lazy Imports**: In Streamlit, it's often better to import heavy libraries inside functions to speed up page loading.
4.  **Session vs. Cookie**: Session state is lost on page refresh. Cookies persist. Always check the cookie at the start of `streamlit_app.py` to restore the session.
5.  **Handling Logout**: When logging out, remember to remove the cookie using `controller.remove("gh_auth_token")` in addition to clearing `st.session_state`.
