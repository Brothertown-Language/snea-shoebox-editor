<!-- Copyright (c) 2026 Brothertown Language -->
# Native Streamlit OAuth2 Reference (GitHub)

This document provides a reference for implementing authentication using Streamlit's native `st.login()`, `st.user`, and `st.logout()` commands (available in Streamlit 1.40+). This is the recommended approach for the SNEA Shoebox Editor.

## Core Commands

### 1. `st.login(provider=None)`
Redirects the user to the identity provider.
- After login, Streamlit stores an identity cookie and then redirects the user back to the homepage of the app in a new session.
- If only one provider is configured in `[auth]`, the `provider` argument is optional.
- If multiple providers are configured, you must specify the provider name as declared in your `secrets.toml`.

### 2. `st.user`
A dict-like object for accessing authenticated user information.
- `st.user.is_logged_in`: A persistent attribute to check for the user's login status.
- Attributes (like `name`, `email`) are available per your identity provider's configuration.
- Information in `st.user` is updated at the beginning of each session.

### 3. `st.logout()`
Removes the identity cookie from the user's browser and redirects them to the homepage of the app in a new session.
- This logs the user out from the current session.
- Streamlit does **not** modify or delete any cookies saved directly by your identity provider (e.g., the user remains logged in to their GitHub account).

## Configuration

Native auth is configured via `.streamlit/secrets.toml` using the `[auth]` dictionary.

### Required Shared Keys
These two values are shared between all OIDC providers in your app and must be declared in the `[auth]` dictionary:
- `redirect_uri`: The URL in your application where users are sent after authorization. For native auth, it must end with the pathname `oauth2callback` (e.g., `http://localhost:8501/oauth2callback`).
- `cookie_secret`: A strong, randomly generated string used to sign the identity cookie.

### Provider Configuration
If you are using only one provider, you can put the remaining properties (`client_id`, `client_secret`, and `server_metadata_url`) directly in `[auth]`.

If you use multiple providers, they should each have a unique name declared in their own sub-dictionaries (e.g., `[auth.github]`, `[auth.google]`).

#### `.streamlit/secrets.toml` Example (Single Provider):
```toml
[auth]
redirect_uri = "http://localhost:8501/oauth2callback"
cookie_secret = "your-very-secure-random-string"
client_id = "your-github-client-id"
client_secret = "your-github-client-secret"
# GitHub requires manual endpoint configuration as it is not fully OIDC-compliant
authorize_url = "https://github.com/login/oauth/authorize"
token_url = "https://github.com/login/oauth/access_token"
```

#### `.streamlit/secrets.toml` Example (Multiple Providers):
```toml
[auth]
redirect_uri = "http://localhost:8501/oauth2callback"
cookie_secret = "your-very-secure-random-string"

[auth.github]
client_id = "xxx"
client_secret = "xxx"
authorize_url = "https://github.com/login/oauth/authorize"
token_url = "https://github.com/login/oauth/access_token"

[auth.google]
client_id = "xxx"
client_secret = "xxx"
server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration"
```

> **Note on GitHub**: Since GitHub is primarily an OAuth2 provider and does not provide a standard OIDC discovery endpoint for user login, you must explicitly set `authorize_url` and `token_url` instead of `server_metadata_url`.

## Implementation Example

```python
import streamlit as st

# Secure your app: Stop execution if not logged in
if not st.user.is_logged_in:
    st.title("Welcome to SNEA Shoebox Editor")
    st.write("Please log in to continue.")
    st.button("Log in with GitHub", on_click=st.login)
    st.stop()

# Application logic for authenticated users
st.title("SNEA Shoebox Editor")
st.sidebar.write(f"Logged in as: **{st.user.name}**")

if st.sidebar.button("Log out"):
    st.logout()

# Main app content...
```

## Session Persistence & Multi-Tab Behavior
- **Identity Cookie**: Streamlit checks for an identity cookie at the beginning of each new session.
- **Auto-Login**: If a user logs in to your app in one tab and opens a new tab, they will automatically be logged in.
- **Logout Scope**: Calling `st.logout()` removes the identity cookie and starts a new session for the current tab. Other already-open sessions will remain logged in until they are refreshed or restart their session.
- **Expiration**: If a user closes the app without logging out, the identity cookie expires after **30 days** (non-configurable). 
- **Expiration Management**: To prevent persistent 30-day authentication, check the expiration information returned by the identity provider in `st.user` and manually call `st.logout()` when needed.

## Identity Provider Requirements
When registering the OAuth application on GitHub:
1.  **Homepage URL**: `http://localhost:8501` (Local) or `https://snea-shoebox-editor.streamlit.app/` (Prod).
2.  **Authorization callback URL**: Must include `/oauth2callback` (e.g., `http://localhost:8501/oauth2callback`).
