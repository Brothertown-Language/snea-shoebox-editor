# Copyright (c) 2026 Brothertown Language
import requests
import time
import os
import streamlit as st
from typing import Optional, Dict, Any

def get_aiven_config() -> Optional[Dict[str, str]]:
    """Retrieve Aiven configuration from Streamlit secrets."""
    try:
        if "aiven" in st.secrets:
            return {
                "project": st.secrets["aiven"]["project_name"],
                "service": st.secrets["aiven"]["service_name"],
                "api_token": st.secrets["aiven"]["api_token"]
            }
    except Exception:
        pass
    return None

def get_service_status(config: Dict[str, str]) -> Optional[str]:
    """Get the current state of the Aiven service."""
    url = f"https://api.aiven.io/v1/project/{config['project']}/service/{config['service']}"
    headers = {"Authorization": f"aivenv1 {config['api_token']}"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("service", {}).get("state")
    except Exception as e:
        st.error(f"Error checking Aiven service status: {e}")
        return None

def start_service(config: Dict[str, str]) -> bool:
    """Trigger the Aiven service to start (power on)."""
    url = f"https://api.aiven.io/v1/project/{config['project']}/service/{config['service']}/status"
    headers = {"Authorization": f"aivenv1 {config['api_token']}"}
    data = {"powered": True}
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        response.raise_for_status()
        return True
    except Exception as e:
        st.error(f"Error starting Aiven service: {e}")
        return False

@st.dialog("Database Starting")
def show_startup_dialog(config: Dict[str, str], initial_status: str):
    """Display a dialog with the database startup status."""
    st.write(f"The production database is currently **{initial_status}**.")
    
    if initial_status == "POWEROFF":
        st.write("Sending start command...")
        if not start_service(config):
            st.error("Failed to send start command. Please contact support.")
            return
        st.write("Start command sent. Waiting for database to become active...")

    # Polling
    max_polls = 30 # 30 * 10s = 5 minutes
    poll_delay = 10
    
    status_placeholder = st.empty()
    progress_bar = st.progress(0)
    
    for i in range(max_polls):
        current_status = get_service_status(config)
        if current_status == "RUNNING":
            status_placeholder.success("Database is now online!")
            progress_bar.progress(100)
            time.sleep(2) # Give user a moment to see success
            st.rerun() # This will dismiss the dialog and reload the page
            return
        
        status_placeholder.info(f"Current Status: **{current_status or 'Unknown'}**\n\nChecking again in {poll_delay}s... (Attempt {i+1}/{max_polls})")
        progress_bar.progress((i + 1) / max_polls)
        time.sleep(poll_delay)
    
    st.error("The production database is taking too long to start. Please try refreshing the page in a few minutes.")
    if st.button("Close"):
        st.rerun()

def ensure_db_alive():
    """Check if DB is alive, start it if not, and show dialog until ready."""
    from src.database import is_production
    
    # Only manage Aiven in production
    if not is_production():
        return

    config = get_aiven_config()
    if not config:
        return

    status = get_service_status(config)
    
    if status == "RUNNING":
        return
    
    if status in ["POWEROFF", "REBUILDING"]:
        if "db_checked" in st.session_state:
            # We already tried to start it in this session
            if status != "RUNNING":
                st.warning(f"Database is still in {status} state. Some features may not work.")
            return

        st.session_state.db_checked = True
        show_startup_dialog(config, status)
    else:
        st.warning(f"Database is in an unexpected state: {status}. It may not be available.")
