# TODO: Implement Persistent OAuth Login

This document outlines the immediate next steps to enable persistent authentication that survives browser reloads and ensures correct permission control.

## 1. Configure Cookie Secret
Add a secure `cookie_secret` to your local secrets to enable encrypted cookie storage by `streamlit-oauth`.

**File:** `.streamlit/secrets.toml`
```toml
[github_oauth]
# ... existing keys ...
cookie_secret = "your-secure-random-string-here"
```

## 2. Enable Cookies in Login Page
Update the `OAuth2Component` initialization to use the secret.

**File:** `src/frontend/pages/login.py`
```python
# Update initialization
oauth2 = OAuth2Component(
    st.secrets["github_oauth"]["client_id"],
    st.secrets["github_oauth"]["client_secret"],
    st.secrets["github_oauth"]["authorize_url"],
    st.secrets["github_oauth"]["token_url"],
    st.secrets["github_oauth"]["redirect_uri"],
    st.secrets["github_oauth"].get("cookie_secret") # Previously None
)
```

## 3. Implement Session Recovery in App Entry Point
Modify `app.py` to check for an existing session cookie at the start. If a valid cookie is found, `authorize_button` will return the token immediately without showing the button.

**File:** `src/frontend/app.py`
```python
def main():
    # ... after st.set_page_config ...
    
    from streamlit_oauth import OAuth2Component
    oauth2 = OAuth2Component(
        st.secrets["github_oauth"]["client_id"],
        st.secrets["github_oauth"]["client_secret"],
        st.secrets["github_oauth"]["authorize_url"],
        st.secrets["github_oauth"]["token_url"],
        st.secrets["github_oauth"]["redirect_uri"],
        st.secrets["github_oauth"].get("cookie_secret")
    )

    if not st.session_state.get("logged_in"):
        # This checks the encrypted cookie automatically
        result = oauth2.authorize_button(
            name="Continue with GitHub",
            redirect_uri=st.secrets["github_oauth"]["redirect_uri"],
            scope="read:user user:email read:org",
            key="oauth_check",
        )
        
        if result and "token" in result:
            st.session_state["auth"] = result
            st.session_state["logged_in"] = True
            # IMPORTANT: Re-fetch user info here to hydrate session state
            # hydration_logic(result["token"]["access_token"])
```

## 4. Ensure Permission Integrity
- **Re-fetch on Recovery:** Do not store full permission sets in the cookie. Store only the token.
- **Hydration:** Implement a utility function (e.g., in `src/frontend/utils.py`) to fetch user profile, orgs, and teams from GitHub using the recovered `access_token`.
- **Validation:** Always use the fresh `user_info` for page-level permission checks.
