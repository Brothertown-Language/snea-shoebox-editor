# Copyright (c) 2026 Brothertown Language
import streamlit as st
import httpx
import os
import re
import json
import time
from typing import Optional, Dict, Any, Tuple, List
import streamlit.components.v1 as components

# Add parent directory to sys.path to import from backend
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.backend.database import get_session, Record, Source, init_db, User
from src.backend.mdf_parser import parse_mdf
from sqlalchemy import func

try:
    from dotenv import load_dotenv
    if os.path.exists(".env"):
        load_dotenv()
except ImportError:
    pass

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
GITHUB_CLIENT_ID = st.secrets.get("github_oauth", {}).get("client_id")
GITHUB_CLIENT_SECRET = st.secrets.get("github_oauth", {}).get("client_secret")
GITHUB_REDIRECT_URI = st.secrets.get("github_oauth", {}).get("redirect_uri")


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
    st.write("Welcome to the SNEA Online Shoebox Editor - A collaborative platform for editing Southern New England Algonquian language records.")
    
    st.divider()
    
    # Login Section
    st.subheader("Authentication")
    st.write("Please log in with your GitHub account to access the editor.")
    
    if not GITHUB_CLIENT_ID:
        st.error("GitHub OAuth Client ID not configured. Please check Streamlit secrets.")
        return

    # Construct GitHub OAuth URL
    state = str(int(time.time()))
    scope = "read:user user:email read:org"
    auth_url = f"https://github.com/login/oauth/authorize?client_id={GITHUB_CLIENT_ID}&redirect_uri={GITHUB_REDIRECT_URI}&scope={scope}&state={state}"
    
    st.link_button("Log in with GitHub", auth_url, type="primary", use_container_width=True)
    
    st.info("Note: Access is restricted to authorized members of the Brothertown Language project.")


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


def _exchange_oauth_token(code: str, state: str) -> Optional[str]:
    """Exchanges OAuth code for access token."""
    try:
        response = httpx.post(
            "https://github.com/login/oauth/access_token",
            headers={"Accept": "application/json"},
            data={
                "client_id": GITHUB_CLIENT_ID,
                "client_secret": GITHUB_CLIENT_SECRET,
                "code": code,
                "redirect_uri": GITHUB_REDIRECT_URI
            },
            timeout=10.0
        )
        if response.status_code == 200:
            return response.json().get("access_token")
        else:
            st.error(f"Failed to exchange token: {response.text}")
    except Exception as e:
        st.error(f"Error during token exchange: {e}")
    return None


def _get_github_user(token: str) -> Optional[Dict[str, Any]]:
    """Fetches user details from GitHub API."""
    try:
        response = httpx.get(
            "https://api.github.com/user",
            headers={"Authorization": f"token {token}", "Accept": "application/json"},
            timeout=10.0
        )
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"Error fetching user: {e}")
    return None


def _store_session(user: Dict[str, Any], token: str) -> None:
    """Stores user session in session_state and optionally localStorage."""
    st.session_state.user = user
    st.session_state.token = token
    
    # Save user to database
    session = get_session()
    try:
        db_user = session.query(User).filter(User.github_id == user.get("id")).first()
        if not db_user:
            db_user = User(
                email=user.get("email") or f"{user.get('login')}@users.noreply.github.com",
                github_id=user.get("id"),
                username=user.get("login"),
                name=user.get("name")
            )
            session.add(db_user)
        
        db_user.last_login = func.now()
        session.commit()
    except Exception as e:
        st.warning(f"Failed to sync user to database: {e}")
    finally:
        session.close()

    # Bridge to localStorage
    user_json = json.dumps(user).replace('"', '\\"')
    st.markdown(f"""
        <script>
            localStorage.setItem("snea_session_token", "{token}");
            localStorage.setItem("snea_session_user", JSON.stringify({json.dumps(user)}));
        </script>
    """, unsafe_allow_html=True)


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
        token = _exchange_oauth_token(code, state)
        if not token:
            st.error("Login failed: Could not exchange OAuth code for access token.")
            return
        
        user = _get_github_user(token)
        if user:
            # Check organization membership (Optional, but recommended)
            # For now, we'll just store the session
            _store_session(user, token)
            st.success(f"Logged in as {user.get('login')}! Redirecting...")
            time.sleep(0.5)
            st.rerun()
        else:
            st.error("Login failed: Could not fetch user details from GitHub.")

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


def _handle_file_upload(source_id: int):
    """Handles MDF file upload and record creation."""
    uploaded_file = st.file_uploader("Upload MDF File", type=["txt", "mdf"])
    if uploaded_file is not None:
        content = uploaded_file.getvalue().decode("utf-8")
        records = parse_mdf(content)
        if not records:
            st.warning("No records found in the uploaded file.")
            return

        session = get_session()
        try:
            count = 0
            for r in records:
                db_record = Record(
                    source_id=source_id,
                    lx=r['lx'],
                    ps=r['ps'],
                    ge=r['ge'],
                    mdf_data=r['mdf_data'],
                    status='draft'
                )
                session.add(db_record)
                count += 1
            session.commit()
            st.success(f"Successfully uploaded {count} records!")
            st.rerun()
        except Exception as e:
            session.rollback()
            st.error(f"Error uploading: {e}")
        finally:
            session.close()


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
                        localStorage.removeItem("snea_session_token");
                        localStorage.removeItem("snea_session_user");
                        console.log("Session cleared from localStorage");
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
    """Fetches total record count from database."""
    session = get_session()
    try:
        count = session.query(func.count(Record.id)).filter(Record.is_deleted == False).scalar()
        return count or 0
    except Exception as e:
        st.error(f"Error fetching count: {e}")
        return 0
    finally:
        session.close()


def _fetch_records(headers: Dict[str, str], limit: int, offset: int) -> List[Dict[str, Any]]:
    """Fetches paginated records from database."""
    session = get_session()
    try:
        records = session.query(Record).filter(Record.is_deleted == False)\
            .order_by(Record.lx)\
            .offset(offset).limit(limit).all()
        
        return [
            {
                "id": r.id,
                "lx": r.lx,
                "ps": r.ps,
                "ge": r.ge,
                "mdf_data": r.mdf_data
            } for r in records
        ]
    except Exception as e:
        st.error(f"Error fetching records: {e}")
        return []
    finally:
        session.close()


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
    """Updates a record in the database."""
    lx, hm, ps, ge = parse_mdf(mdf_data)
    
    if not lx:
        st.error("Missing \\lx tag in record.")
        return
    
    session = get_session()
    try:
        record = session.query(Record).filter(Record.id == record_id).first()
        if not record:
            st.error("Record not found.")
            return

        # Update fields
        record.lx = lx
        record.ps = ps
        record.ge = ge
        record.mdf_data = mdf_data
        record.updated_by = st.session_state.user.get("login") if "user" in st.session_state else "anonymous"
        record.current_version += 1
        
        session.commit()
        st.success("Record updated!")
        st.rerun()
    except Exception as e:
        session.rollback()
        st.error(f"Error updating: {e}")
    finally:
        session.close()


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

    # Render sidebar
    _render_sidebar(user, current_page, page_size, total_count, len(records), offset)

    # Admin: File Upload Tool
    if st.sidebar.checkbox("Show Upload Tool"):
        st.sidebar.markdown("---")
        st.sidebar.subheader("Import Records")
        
        # Get list of sources
        session = get_session()
        sources = session.query(Source).all()
        session.close()
        
        if not sources:
            st.sidebar.warning("No sources defined in database.")
            if st.sidebar.button("Create Default Source"):
                session = get_session()
                default_source = Source(name="Natick/Trumbull", description="Trumbull's Natick Dictionary")
                session.add(default_source)
                session.commit()
                session.close()
                st.rerun()
        else:
            source_options = {s.name: s.id for s in sources}
            selected_source_name = st.sidebar.selectbox("Target Source", options=list(source_options.keys()))
            source_id = source_options[selected_source_name]
            _handle_file_upload(source_id)

    if not records and current_page == 0:
        st.info("No records found.")
        return

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
    # Attempt to restore session from localStorage if not already in session_state
    if "user" not in st.session_state:
        # Use a component to read from localStorage and pass to Python
        # Bridge JS and Python
        session_check_html = """
        <div id="session-loader" style="display:none"></div>
        <script>
            (function() {
                const token = localStorage.getItem("snea_session_token");
                const userJson = localStorage.getItem("snea_session_user");
                
                if (token && userJson) {
                    console.log("Found session in localStorage, attempting restore");
                    // Store in a temporary location that Python can check
                    window.parent.postMessage({
                        type: "snea_session_restore",
                        token: token,
                        user: userJson
                    }, "*");
                } else {
                    console.log("No session found in localStorage");
                }
            })();
        </script>
        """
        components.html(session_check_html, height=0)
        
        # Try to get session from query params if passed by the JS bridge
        # This is a fallback mechanism
        query_params = get_query_params()
        if "session_token" in query_params and "session_user" in query_params:
            try:
                token = query_params["session_token"]
                user_json = query_params["session_user"]
                user = json.loads(user_json)
                
                # Verify token with backend
                headers = {"Authorization": f"Bearer {token}"}
                user_res = httpx.get("/api/me", headers=headers, timeout=5.0)
                if user_res.status_code == 200:
                    st.session_state.user = user_res.json()
                    st.session_state.token = token
                    # Clean up query params
                    set_query_params(session_token=None, session_user=None)
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
    try:
        init_db()
    except Exception as e:
        # Fallback for local dev if DATABASE_URL is missing
        pass
    main()
