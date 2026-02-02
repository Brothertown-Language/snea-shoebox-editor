# Copyright (c) 2026 Brothertown Language
import streamlit as st
import httpx
import os
import re
import json
import time
from typing import Optional, Dict, Any, Tuple, List
import streamlit.components.v1 as components
try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

# Set page config for compact wide layout
st.set_page_config(
    page_title="SNEA Shoebox Editor",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load environment variables for local development
if load_dotenv:
    load_dotenv()

# Configuration
# For local development, we use GITHUB_CLIENT_ID. 
# Production (Cloudflare Pages) would use SNEA_GITHUB_CLIENT_ID if configured there,
# but Streamlit here is primarily for local dev or simple hosting.
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")


def set_query_params(**params: Optional[Any]) -> None:
    """Updates the URL query parameters."""
    for k, v in params.items():
        if v is None:
            if k in st.query_params:
                del st.query_params[k]
        else:
            st.query_params[k] = str(v)

def get_query_params() -> Dict[str, Any]:
    """Returns the current query parameters."""
    return st.query_params


def login_page() -> None:
    """Renders the login page with GitHub OAuth button."""
    st.title("SNEA Online Shoebox Editor")
    st.write("Welcome to the SNEA Online Shoebox Editor. Please log in to continue.")
    
    if st.button("Log in with GitHub"):
        # In Stlite, we can't easily do a meta-refresh redirect from a button click 
        # inside the iframe easily without window.location.href.
        # But we can try the same markdown trick or use a link.
        try:
            with st.spinner(f"Connecting to backend..."):
                response = httpx.get("/api/oauth/login", timeout=5.0)
            
            if response.status_code == 200:
                data = response.json()
                auth_url = data.get("authorize_url") or data.get("url")
                
                if auth_url:
                    # In Stlite, we are already in the browser. 
                    # We need to escape the sandboxed iframe if we are in one,
                    # but Stlite mountable usually handles this.
                    st.markdown(f'''
                        <script>
                            window.parent.location.href = "{auth_url}";
                        </script>
                        <a href="{auth_url}" target="_parent">Click here to login with GitHub</a> (Redirecting...)
                    ''', unsafe_allow_html=True)
                else:
                    st.error("Failed to get authorization URL from backend.")
            else:
                st.error(f"Backend error: {response.status_code}")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")


def _extract_oauth_params() -> Tuple[Optional[str], Optional[str]]:
    """Extracts and normalizes OAuth code and state from query parameters."""
    query_params = st.query_params
    if "code" not in query_params:
        return None, None
    
    code_val = query_params.get("code")
    state_val = query_params.get("state")
    
    # In newer streamlit versions, get() returns a string or list
    if isinstance(code_val, list):
        code_val = code_val[0]
    if isinstance(state_val, list):
        state_val = state_val[0]
    
    return code_val, state_val


def _clear_oauth_params() -> None:
    """Removes OAuth code and state from query parameters."""
    if "code" in st.query_params or "state" in st.query_params:
        new_params = {k: v for k, v in st.query_params.items() if k not in ("code", "state")}
        st.query_params.clear()
        for k, v in new_params.items():
            st.query_params[k] = v


def _exchange_oauth_token(code: str, state: str) -> Optional[httpx.Response]:
    """Exchanges OAuth code for access token via backend."""
    try:
        response = httpx.post(
            "/api/oauth/callback",
            json={"code": code, "state": state},
            timeout=30.0
        )
        return response
    except Exception as e:
        st.error(f"Error during login: {e}")
        return None


def _store_session(user: Dict[str, Any], token: str) -> None:
    """Stores user session in session state and browser cookie."""
    st.session_state.user = user
    st.session_state.token = token
    
    # Set cookie for persistence (30 days)
    st.markdown(
        f"""
        <div style="display:none">
            <script>
                document.cookie = "session={token}; Max-Age={30*24*60*60}; path=/; SameSite=Lax";
            </script>
        </div>
        """,
        unsafe_allow_html=True
    )


def _display_login_error(response: httpx.Response) -> None:
    """Displays login error with details and traceback if available."""
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
    except Exception:
        st.error(f"Login failed: {response.status_code}")
        st.text(f"Raw Response: {response.text}")


def handle_callback() -> None:
    """Handles OAuth callback by exchanging code for token and storing session."""
    code, state = _extract_oauth_params()
    if not code or not state:
        return
    
    _clear_oauth_params()
    
    with st.spinner("Logging in..."):
        response = _exchange_oauth_token(code, state)
        if not response:
            return
        
        if response.status_code == 200:
            data = response.json()
            user = data.get("user")
            token = data.get("token")
            
            if user and token:
                _store_session(user, token)
                st.success("Logged in successfully! Redirecting...")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Login failed: Backend returned success but no user data.")
                st.json(data)
        else:
            _display_login_error(response)

def parse_mdf(mdf_text: str) -> Tuple[str, int, str, str]:
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


def _render_sidebar(user: Dict[str, Any], current_page: int, page_size: int, 
                    total_count: int, records_count: int, offset: int) -> None:
    """Renders sidebar with navigation, user info, logout, and pagination controls."""
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
            st.markdown(
                """
                <div style="display:none">
                    <script>
                        document.cookie = "session=; Max-Age=0; path=/; SameSite=Lax";
                    </script>
                </div>
                """,
                unsafe_allow_html=True
            )
            time.sleep(0.5)
            st.rerun()

        # Pagination controls
        st.divider()
        st.write(f"Page {current_page + 1}")
        col_prev, col_next = st.columns(2)
        if col_prev.button("⬅️ Previous", disabled=(current_page <= 0), use_container_width=True):
            set_query_params(page=current_page - 1)
            st.rerun()
        
        has_more = records_count == page_size and (offset + page_size) < total_count
        if col_next.button("Next ➡️", disabled=not has_more, use_container_width=True):
            set_query_params(page=current_page + 1)
            st.rerun()
        
        if total_count > 0:
            st.caption(f"Showing {offset + 1} - {offset + records_count} of {total_count} records")


def _fetch_total_count(headers: Dict[str, str]) -> int:
    """Fetches total record count from backend."""
    try:
        count_res = httpx.get("/api/records/count", headers=headers, timeout=5.0)
        if count_res.status_code == 200:
            return count_res.json().get("count", 0)
    except Exception:
        pass
    return 0


def _fetch_records(headers: Dict[str, str], limit: int, offset: int) -> List[Dict[str, Any]]:
    """Fetches paginated records from backend."""
    try:
        response = httpx.get(f"/api/records?limit={limit}&offset={offset}", headers=headers, timeout=10.0)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            st.error("Session expired. Please log in again.")
            del st.session_state.user
            st.rerun()
        else:
            st.error(f"Failed to fetch records: {response.status_code}")
    except Exception as e:
        st.error(f"Error fetching records: {e}")
    return []


def _render_records_list(records: List[Dict[str, Any]]) -> None:
    """Renders list view of records with edit buttons."""
    st.subheader("Records List")
    for r in records:
        col_lx, col_ps, col_ge, col_act = st.columns([2, 1, 4, 1])
        col_lx.write(r.get("lx"))
        col_ps.write(r.get("ps"))
        col_ge.write(r.get("ge"))
        if col_act.button("Edit", key=f"edit_{r['id']}"):
            set_query_params(id=r["id"], view="edit")
            st.rerun()


def _find_default_record_index(records: List[Dict[str, Any]], selected_record_id: Optional[str]) -> int:
    """Finds the index of the selected record in the list."""
    if not selected_record_id:
        return 0
    
    try:
        target_id = int(selected_record_id)
        for i, r in enumerate(records):
            if isinstance(r, dict) and r.get("id") == target_id:
                return i
    except (ValueError, TypeError):
        pass
    return 0


def _update_record(record_id: int, mdf_data: str, headers: Dict[str, str]) -> None:
    """Updates a record via backend API."""
    lx, hm, ps, ge = parse_mdf(mdf_data)
    
    if not lx:
        st.error("Missing \\lx tag in record.")
        return
    
    update_payload = {
        "lx": lx,
        "ps": ps,
        "ge": ge,
        "mdf_data": mdf_data
    }
    
    try:
        update_res = httpx.post(
            f"/api/records/{record_id}",
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


def _render_record_editor(records: List[Dict[str, Any]], query_params: Dict[str, Any], 
                          headers: Dict[str, str]) -> None:
    """Renders record editor with selector and edit form."""
    record_options = {f"{r['lx']} ({r['ps'] or 'no ps'})": r for r in records if isinstance(r, dict)}
    selected_record_id = query_params.get("id")
    default_index = _find_default_record_index(records, selected_record_id)

    col_sel, col_btn = st.columns([8, 2])
    with col_sel:
        selected_label = st.selectbox(
            "Select Record", 
            options=list(record_options.keys()), 
            index=default_index,
            label_visibility="collapsed",
            key="record_selector"
        )
    
    if not selected_label:
        return
    
    selected_record = record_options[selected_label]
    
    # Sync URL with selected record
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
            _update_record(selected_record['id'], mdf_data, headers)


def main_app() -> None:
    """Main application interface for authenticated users."""
    user = st.session_state.get("user")
    token = st.session_state.get("token")
    
    if not user:
        st.error("User session not found. Please log in again.")
        if st.button("Go to Login"):
            if "user" in st.session_state:
                del st.session_state.user
            st.rerun()
        return

    query_params = get_query_params()
    page_size = 50
    current_page = int(query_params.get("page", 0))
    offset = current_page * page_size
    headers = {"Authorization": f"Bearer {token}"} if token else {}

    # Fetch data
    total_count = _fetch_total_count(headers)
    records = _fetch_records(headers, page_size, offset)

    if not records and current_page == 0:
        st.info("No records found.")
        return

    # Render sidebar
    _render_sidebar(user, current_page, page_size, total_count, len(records), offset)

    # View routing
    view = query_params.get("view", "edit")

    if view == "list":
        _render_records_list(records)
    elif view == "login":
        set_query_params(view="list")
        st.rerun()
    else:
        _render_record_editor(records, query_params, headers)

def main() -> None:
    """Main entry point for the application."""
    # Attempt to restore session from cookie if not already in session_state
    if "user" not in st.session_state:
        try:
            # In Stlite, we can access cookies directly via browser APIs if needed,
            # but Streamlit's context.cookies is the standard way.
            cookies = getattr(st, "context", None) and getattr(st.context, "cookies", None)
            
            if cookies and "session" in cookies:
                token = cookies["session"]
                # Verify token with backend
                try:
                    # Relative path works in Stlite httpx
                    headers = {"Authorization": f"Bearer {token}"}
                    # Fetch user info from /api/me
                    user_res = httpx.get("/api/me", headers=headers, timeout=5.0)
                    if user_res.status_code == 200:
                        st.session_state.user = user_res.json()
                        st.session_state.token = token
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
