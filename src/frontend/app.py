# Copyright (c) 2026 Brothertown Language
import streamlit as st
import httpx
import os
from dotenv import load_dotenv

# Load environment variables for local development
load_dotenv()

# Configuration
# For local development, we use GITHUB_CLIENT_ID. 
# Production (Cloudflare Pages) would use SNEA_GITHUB_CLIENT_ID if configured there,
# but Streamlit here is primarily for local dev or simple hosting.
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")

# BACKEND_URL priority: env var > inferred from current host (if on michael-conrad.com) > localhost
# Note: Streamlit performs 'httpx' calls from the SERVER, but browser-redirects from the CLIENT.
# For Docker, the server needs http://backend:8787 while the client needs http://localhost:8787.
# We will use BACKEND_URL for server-side calls and a dynamic logic for client-side.

def get_backend_url(client_side=False):
    # 1. Check environment variable first (highest priority, allows manual override)
    env_backend = os.getenv("BACKEND_URL")
    if env_backend:
        return env_backend.rstrip('/')

    # 2. Try to infer from environment
    is_local = os.getenv("STREAMLIT_SERVER_PORT") is not None or os.getenv("PROD") != "true"
    
    if is_local:
        # If we are inside Docker, the server calls 'backend:8787'
        # but the browser (client_side) must call 'localhost:8787'
        if client_side:
            return "http://localhost:8787"
        
        # Heuristic for being inside Docker
        if os.path.exists("/.dockerenv") or os.getenv("HOSTNAME") == "web":
            return "http://backend:8787"
        
        return "http://localhost:8787"
        
    # 3. Default production URL for Brothertown SNEA project
    return "https://snea-backend.michael-conrad.com"

# Server-side calls use this
BACKEND_URL = get_backend_url(client_side=False)
# Browser-side redirects should use get_backend_url(client_side=True)

st.set_page_config(page_title="SNEA Shoebox Editor", page_icon="📚")

def login_page():
    st.title("SNEA Online Shoebox Editor")
    st.write("Welcome to the SNEA Online Shoebox Editor. Please log in to continue.")
    
    # GitHub login button
    if st.button("Log in with GitHub"):
        # Server-side check
        try:
            with st.spinner(f"Connecting to backend..."):
                # We use the internal BACKEND_URL (e.g., http://backend:8787)
                response = httpx.get(f"{BACKEND_URL}/api/oauth/login", timeout=5.0)
            
            if response.status_code == 200:
                data = response.json()
                auth_url = data.get("authorize_url") or data.get("url")
                
                # If we are in Docker, the backend gave us an authorize_url.
                # It contains a redirect_uri.
                # If backend used heuristic correctly, it's http://localhost:8501
                
                if auth_url:
                    st.markdown(f'<meta http-equiv="refresh" content="0; url={auth_url}">', unsafe_allow_html=True)
                    st.write(f"Redirecting to GitHub... If not redirected, [click here]({auth_url})")
                else:
                    st.error("Failed to get authorization URL from backend.")
            else:
                st.error(f"Backend error: {response.status_code}")
                with st.expander("Debug Info"):
                    st.write(f"URL: {BACKEND_URL}/api/oauth/login")
                    st.text(f"Response: {response.text}")
        except httpx.ConnectError:
            st.error(f"Could not connect to backend at **{BACKEND_URL}**.")
            st.info("This usually means the backend server is not running or the URL is incorrect.")
            with st.expander("Troubleshooting"):
                st.write(f"Current BACKEND_URL (Server-side): `{BACKEND_URL}`")
                st.write(f"Inferred Backend URL (Client-side): `{get_backend_url(client_side=True)}`")
                st.write("1. If running locally with Docker, ensure both `web` and `backend` containers are healthy.")
                st.write("2. If in production, check if the backend worker is deployed and the custom domain is active.")
                st.write("3. You can override the backend URL by setting the `BACKEND_URL` environment variable.")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
            with st.expander("Technical Details"):
                st.exception(e)

def handle_callback():
    query_params = st.query_params
    if "code" in query_params:
        # Coerce possible list/tuple values to simple strings
        code_val = query_params.get("code")
        state_val = query_params.get("state")
        
        # In newer streamlit versions, get() returns a string or list
        if isinstance(code_val, list):
            code_val = code_val[0]
        if isinstance(state_val, list):
            state_val = state_val[0]

        code = code_val
        state = state_val
        # Clear query params so we don't keep trying to log in with the same code
        # In newer Streamlit versions, st.query_params.clear() might be better
        # but let's just remove 'code' to be safe and precise
        if "code" in st.query_params or "state" in st.query_params:
            new_params = {k: v for k, v in st.query_params.items() if k not in ("code", "state")}
            st.query_params.clear()
            for k, v in new_params.items():
                st.query_params[k] = v
        
        with st.spinner("Logging in..."):
            try:
                response = httpx.post(
                    f"{BACKEND_URL}/api/oauth/callback",
                    json={"code": code, "state": state},
                    timeout=30.0 # Token exchange can be slow
                )
                if response.status_code == 200:
                    data = response.json()
                    user = data.get("user")
                    token = data.get("token")
                    if user:
                        st.session_state.user = user
                        st.session_state.token = token
                        st.success("Logged in successfully!")
                        st.rerun()
                    else:
                        st.error(f"Login failed: Backend returned success but no user data.")
                        st.json(data)
                else:
                    try:
                        error_data = response.json()
                        st.error(f"Login failed: {error_data.get('error', response.text)}")
                        
                        # Show all extra fields for debugging
                        extra_fields = {k: v for k, v in error_data.items() if k not in ["error", "traceback"]}
                        if extra_fields:
                            with st.expander("Error Details"):
                                st.json(extra_fields)
                                
                        if "traceback" in error_data:
                            with st.expander("Backend Traceback"):
                                st.code(error_data["traceback"])
                    except Exception as json_err:
                        st.error(f"Login failed: {response.status_code}")
                        st.text(f"Raw Response: {response.text}")
            except Exception as e:
                st.error(f"Error during login: {e}")

def main_app():
    user = st.session_state.get("user")
    token = st.session_state.get("token")
    if not user:
        st.error("User session not found. Please log in again.")
        if st.button("Go to Login"):
            if "user" in st.session_state:
                del st.session_state.user
            st.rerun()
        return

    st.sidebar.write(f"Logged in as: {user.get('name', user.get('login', 'Unknown'))}")
    if st.sidebar.button("Logout"):
        if "user" in st.session_state:
            del st.session_state.user
        if "token" in st.session_state:
            del st.session_state.token
        st.rerun()
        
    st.title("SNEA Shoebox Editor")

    # Fetch records
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    try:
        response = httpx.get(f"{BACKEND_URL}/api/records", headers=headers, timeout=10.0)
        if response.status_code == 200:
            records = response.json()
        elif response.status_code == 401:
            st.error("Session expired. Please log in again.")
            del st.session_state.user
            st.rerun()
            return
        else:
            st.error(f"Failed to fetch records: {response.status_code}")
            records = []
    except Exception as e:
        st.error(f"Error fetching records: {e}")
        records = []

    if not records:
        st.info("No records found.")
        return

    # Record selection
    record_options = {f"{r['lx']} ({r['ps'] or 'no ps'})": r for r in records if isinstance(r, dict)}
    selected_label = st.selectbox("Select a record to edit", options=list(record_options.keys()))
    
    if selected_label:
        selected_record = record_options[selected_label]
        
        st.subheader(f"Editing: {selected_record['lx']}")
        
        with st.form("edit_record"):
            lx = st.text_input("Lexeme (\lx)", value=selected_record.get("lx", ""))
            ps = st.text_input("Part of Speech (\ps)", value=selected_record.get("ps", ""))
            ge = st.text_input("English Gloss (\ge)", value=selected_record.get("ge", ""))
            mdf_data = st.text_area("Full MDF Data", value=selected_record.get("mdf_data", ""), height=200)
            
            submitted = st.form_submit_button("Save Changes")
            if submitted:
                update_payload = {
                    "lx": lx,
                    "ps": ps,
                    "ge": ge,
                    "mdf_data": mdf_data
                }
                try:
                    update_res = httpx.post(
                        f"{BACKEND_URL}/api/records/{selected_record['id']}",
                        json=update_payload,
                        headers=headers,
                        timeout=10.0
                    )
                    if update_res.status_code == 200:
                        st.success("Record updated successfully!")
                        st.rerun()
                    else:
                        st.error(f"Failed to update record: {update_res.text}")
                except Exception as e:
                    st.error(f"Error updating record: {e}")

def main():
    # If "user" is in session state but is None, remove it
    if "user" in st.session_state and st.session_state.user is None:
        del st.session_state.user
        
    if "user" not in st.session_state:
        # Check if we are in the middle of an OAuth callback
        if "code" in st.query_params:
            handle_callback()
        else:
            login_page()
    else:
        main_app()

if __name__ == "__main__":
    main()
