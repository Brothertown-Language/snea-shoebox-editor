# Copyright (c) 2026 Brothertown Language
import streamlit as st
import httpx
import os
import re
import json
import streamlit.components.v1 as components
from dotenv import load_dotenv

# Set page config for compact wide layout
st.set_page_config(
    page_title="SNEA Shoebox Editor",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

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


def set_query_params(**params):
    """Updates the URL query parameters."""
    for k, v in params.items():
        if v is None:
            if k in st.query_params:
                del st.query_params[k]
        else:
            st.query_params[k] = str(v)

def get_query_params():
    """Returns the current query parameters."""
    return st.query_params


def login_page():
    # Title and welcome message
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
                        # Set cookie for persistence (30 days)
                        # We use a combined approach: try to set it, and don't rerun immediately 
                        # to give the component time to render.
                        components.html(
                            f"""
                            <script>
                                console.log("Attempting to set session cookie...");
                                try {{
                                    window.parent.document.cookie = "session={token}; Max-Age={30*24*60*60}; path=/; SameSite=Lax";
                                    console.log("Successfully set session cookie in window.parent");
                                }} catch (e) {{
                                    console.error("Failed to set cookie in window.parent:", e);
                                    document.cookie = "session={token}; Max-Age={30*24*60*60}; path=/; SameSite=Lax";
                                    console.log("Set session cookie in iframe instead");
                                }}
                                // Inform Streamlit that we are done
                                window.parent.postMessage({{"type": "streamlit:set_cookie_done"}}, "*");
                            </script>
                            """,
                            height=0
                        )
                        st.success("Logged in successfully! Redirecting...")
                        # A brief pause to allow the JS to run
                        import time
                        time.sleep(1)
                        st.rerun()
                        # Auto-rerun after a small delay might be tricky in Streamlit 
                        # so we'll just wait for the user to click or the next heartbeat
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

def parse_mdf(mdf_text):
    """Simple MDF parser to extract lx, hm, ps, ge."""
    lx = ""
    hm = 1
    ps = ""
    ge = ""
    
    # Extract \lx
    lx_match = re.search(r'^\\lx\s+(.*)$', mdf_text, re.MULTILINE)
    if lx_match:
        lx = lx_match.group(1).strip()
        
    # Extract \hm
    hm_match = re.search(r'^\\hm\s+(\d+)$', mdf_text, re.MULTILINE)
    if hm_match:
        try:
            hm = int(hm_match.group(1).strip())
        except ValueError:
            hm = 1

    # Extract \ps
    ps_match = re.search(r'^\\ps\s+(.*)$', mdf_text, re.MULTILINE)
    if ps_match:
        ps = ps_match.group(1).strip()
        
    # Extract \ge
    ge_match = re.search(r'^\\ge\s+(.*)$', mdf_text, re.MULTILINE)
    if ge_match:
        ge = ge_match.group(1).strip()
        
    return lx, hm, ps, ge

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

    # Move navigation and additional info to sidebar
    query_params = get_query_params()
    with st.sidebar:
        st.title("SNEA Editor")
        st.info("Record Selection & Tools")
        
        # Navigation
        if st.button("📚 Records List", use_container_width=True):
            set_query_params(view="list", id=None)
            st.rerun()
        
        if st.button("📝 Editor", use_container_width=True):
            set_query_params(view="edit")
            st.rerun()

        st.divider()
        st.write("Logged in as:")
        st.write(f"**{user.get('name', user.get('login', 'Unknown'))}**")
        
        if st.button("Log out", key="sidebar_logout"):
            if "user" in st.session_state:
                del st.session_state.user
            if "token" in st.session_state:
                del st.session_state.token
            components.html(
                """
                <script>
                    try {
                        window.parent.document.cookie = "session=; Max-Age=0; path=/; SameSite=Lax";
                    } catch (e) {
                        document.cookie = "session=; Max-Age=0; path=/; SameSite=Lax";
                    }
                </script>
                """,
                height=0
            )
            # A brief pause to allow the JS to run
            import time
            time.sleep(0.5)
            st.rerun()

    # Pagination state
    page_size = 50
    current_page = int(query_params.get("page", 0))
    offset = current_page * page_size

    # Fetch total record count
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    total_count = 0
    try:
        count_res = httpx.get(f"{BACKEND_URL}/api/records/count", headers=headers, timeout=5.0)
        if count_res.status_code == 200:
            total_count = count_res.json().get("count", 0)
    except Exception:
        pass

    # Fetch records for current page
    try:
        response = httpx.get(f"{BACKEND_URL}/api/records?limit={page_size}&offset={offset}", headers=headers, timeout=10.0)
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

    if not records and current_page == 0:
        st.info("No records found.")
        return

    # Pagination controls in sidebar
    with st.sidebar:
        st.divider()
        st.write(f"Page {current_page + 1}")
        col_prev, col_next = st.columns(2)
        if col_prev.button("⬅️ Previous", disabled=(current_page <= 0), use_container_width=True):
            set_query_params(page=current_page - 1)
            st.rerun()
        
        has_more = len(records) == page_size and (offset + page_size) < total_count
        if col_next.button("Next ➡️", disabled=not has_more, use_container_width=True):
            set_query_params(page=current_page + 1)
            st.rerun()
        
        if total_count > 0:
            st.caption(f"Showing {offset + 1} - {offset + len(records)} of {total_count} records")

    # View routing
    view = query_params.get("view", "edit")

    if view == "list":
        st.subheader("Records List")
        for r in records:
            col_lx, col_ps, col_ge, col_act = st.columns([2, 1, 4, 1])
            col_lx.write(r.get("lx"))
            col_ps.write(r.get("ps"))
            col_ge.write(r.get("ge"))
            if col_act.button("Edit", key=f"edit_{r['id']}"):
                set_query_params(id=r["id"], view="edit")
                st.rerun()
        return
    elif view == "login":
        # If user is somehow in main_app with view=login, redirect to list
        set_query_params(view="list")
        st.rerun()

    # Record selection in a compact row
    record_options = {f"{r['lx']} ({r['ps'] or 'no ps'})": r for r in records if isinstance(r, dict)}
    
    # Routing: check if record_id is in query params
    selected_record_id = query_params.get("id")
    
    # Find record by ID from hash params if available
    default_index = 0
    if selected_record_id:
        try:
            target_id = int(selected_record_id)
            for i, (label, record) in enumerate(record_options.items()):
                if record.get("id") == target_id:
                    default_index = i
                    break
        except (ValueError, TypeError):
            pass

    col_sel, col_btn = st.columns([8, 2])
    with col_sel:
        selected_label = st.selectbox(
            "Select Record", 
            options=list(record_options.keys()), 
            index=default_index,
            label_visibility="collapsed",
            key="record_selector"
        )
    
    if selected_label:
        selected_record = record_options[selected_label]
        
        # Sync URL with selected record (non-triggering)
        current_id = str(selected_record.get("id"))
        if current_id != query_params.get("id") or query_params.get("view") != "edit":
            set_query_params(id=current_id, view="edit")

        # Raw MDF Editor
        with st.form("edit_record", clear_on_submit=False):
            mdf_data = st.text_area(
                "MDF Record", 
                value=selected_record.get("mdf_data", ""), 
                height=400,
                label_visibility="collapsed"
            )
            
            submitted = st.form_submit_button("Save Record", use_container_width=True)
            if submitted:
                # Parse lx, ps, ge from raw text
                lx, hm, ps, ge = parse_mdf(mdf_data)
                
                if not lx:
                    st.error("Missing \\lx tag in record.")
                else:
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
                            st.success("Record updated!")
                            st.rerun()
                        else:
                            st.error(f"Failed to update: {update_res.text}")
                    except Exception as e:
                        st.error(f"Error updating: {e}")

def main():
    # Attempt to restore session from cookie if not already in session_state
    if "user" not in st.session_state:
        # Streamlit 1.30+ supports st.context.cookies
        try:
            cookies = getattr(st, "context", None) and getattr(st.context, "cookies", None)
            if not cookies:
                # Fallback for some environments or older versions
                try:
                    from streamlit.web.server.websocket_headers import _get_websocket_headers
                    headers = _get_websocket_headers()
                    if headers and "Cookie" in headers:
                        cookie_str = headers["Cookie"]
                        cookies = {c.split("=")[0].strip(): c.split("=")[1].strip() for c in cookie_str.split(";") if "=" in c}
                except Exception:
                    pass

            if cookies and "session" in cookies:
                token = cookies["session"]
                # Verify token with backend
                try:
                    # Use the internal BACKEND_URL for server-side verification
                    headers = {"Authorization": f"Bearer {token}"}
                    # Fetch user info from /api/me
                    user_res = httpx.get(f"{BACKEND_URL}/api/me", headers=headers, timeout=5.0)
                    if user_res.status_code == 200:
                        st.session_state.user = user_res.json()
                        st.session_state.token = token
                        # No st.rerun() here to avoid potential loops, 
                        # but we have set the state so main_app will be called
                except Exception:
                    pass
        except Exception:
            pass

    # If "user" is in session state but is None, remove it
    if "user" in st.session_state and st.session_state.user is None:
        del st.session_state.user

    # Debug: display current cookie status in an expander if in dev mode
    # if os.getenv("DEBUG") == "true":
    #    with st.expander("Session Debug"):
    #        st.write(f"Session State User: {st.session_state.get('user') is not None}")
    #        st.write(f"Session State Token: {st.session_state.get('token') is not None}")

    query_params = get_query_params()
        
    if "user" not in st.session_state:
        # Check if we are in the middle of an OAuth callback
        # OAuth callbacks usually use query parameters (code, state)
        if "code" in st.query_params:
            handle_callback()
        elif query_params.get("view") == "login" or not query_params:
            login_page()
        else:
            # If they have a view but no user, they still need to login
            login_page()
    else:
        main_app()

if __name__ == "__main__":
    main()
