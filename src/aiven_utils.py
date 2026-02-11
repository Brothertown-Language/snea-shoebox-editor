# Copyright (c) 2026 Brothertown Language
# <!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
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

def get_service_info(config: Dict[str, str]) -> Optional[Dict[str, Any]]:
    """Get the full information of the Aiven service."""
    url = f"https://api.aiven.io/v1/project/{config['project']}/service/{config['service']}"
    headers = {"Authorization": f"aivenv1 {config['api_token']}"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 404:
            return None
        response.raise_for_status()
        data = response.json()
        return data.get("service")
    except Exception as e:
        if "404" not in str(e):
            st.error(f"Error checking Aiven service status: {e}")
        return None

def get_service_status(config: Dict[str, str]) -> Optional[str]:
    """Get the current state of the Aiven service."""
    info = get_service_info(config)
    return info.get("state") if info else None

def start_service(config: Dict[str, str]) -> bool:
    """Trigger the Aiven service to start (power on)."""
    url = f"https://api.aiven.io/v1/project/{config['project']}/service/{config['service']}"
    headers = {"Authorization": f"aivenv1 {config['api_token']}"}
    data = {"powered": True}
    
    try:
        response = requests.put(url, headers=headers, json=data, timeout=10)
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
    max_polls = 60 # 60 * 10s = 10 minutes
    poll_delay = 10
    
    status_placeholder = st.empty()
    progress_bar = st.progress(0)
    
    for i in range(max_polls):
        current_status = get_service_status(config)
        
        # Also check DNS
        dns_ok = True
        if current_status == "RUNNING":
            from src.frontend.utils import verify_dns
            from urllib.parse import urlparse
            from src.database import get_db_url
            url = get_db_url()
            if url:
                parsed = urlparse(url)
                host = parsed.hostname
                if host:
                    dns_ok, _, _, _ = verify_dns(host)
        
        if current_status == "RUNNING" and dns_ok:
            status_placeholder.success("Database is now online!")
            progress_bar.progress(100)
            time.sleep(2) # Give user a moment to see success
            st.rerun() # This will dismiss the dialog and reload the page
            return
        
        display_status = current_status
        if current_status == "RUNNING" and not dns_ok:
            display_status = "RUNNING (Waiting for DNS)"
        
        status_placeholder.info(f"Current Status: **{display_status or 'Unknown'}**\n\nChecking again in {poll_delay}s... (Attempt {i+1}/{max_polls})")
        progress_bar.progress((i + 1) / max_polls)
        time.sleep(poll_delay)
    
    # If we reached here, polling timed out
    if current_status == "REBUILDING":
        st.rerun()
        
    st.error("The production database is taking too long to start. Please try refreshing the page in a few minutes.")

@st.dialog("Missing Secrets")
def show_secrets_missing_dialog(missing_secrets: list[str]):
    """Display a dialog listing missing mandatory secrets."""
    st.error("The application cannot start because one or more mandatory secrets are missing.")
    st.write("Please ensure the following secrets are configured in Streamlit Cloud or `.streamlit/secrets.toml`:")
    for secret in missing_secrets:
        st.markdown(f"- `{secret}`")
    
    st.info("After adding the secrets, please refresh the page.")
    if st.button("I've added the secrets, refresh now"):
        st.rerun()

def ensure_secrets_present():
    """Verify that all mandatory secrets are present. Blocks execution if any are missing."""
    # Mandatory secrets for the application to function
    # Note: 'connections.postgresql.url' is checked via src.database.get_db_url()
    # but we can check the base keys here.
    
    mandatory_secrets = [
        "aiven",
        "github_oauth",
        "connections"
    ]
    
    missing = []
    for secret in mandatory_secrets:
        try:
            if secret not in st.secrets:
                missing.append(secret)
            else:
                # Basic structure check
                if secret == "aiven":
                    keys = ["project_name", "service_name", "api_token"]
                    for k in keys:
                        if k not in st.secrets["aiven"]:
                            missing.append(f"aiven.{k}")
                elif secret == "github_oauth":
                    keys = ["client_id", "client_secret", "authorize_url", "token_url", "redirect_uri"]
                    for k in keys:
                        if k not in st.secrets["github_oauth"]:
                            missing.append(f"github_oauth.{k}")
                elif secret == "connections":
                    if "postgresql" not in st.secrets["connections"] or "url" not in st.secrets["connections"]["postgresql"]:
                        missing.append("connections.postgresql.url")
        except Exception:
            missing.append(secret)

    if missing:
        show_secrets_missing_dialog(missing)
        st.stop()

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
    
    # Try DNS resolution first as a quick check
    if status == "RUNNING":
        from src.frontend.utils import verify_dns
        from urllib.parse import urlparse
        from src.database import get_db_url
        
        # In production, we expect DNS failures if service was recently started
        url = get_db_url()
        if url:
            parsed = urlparse(url)
            host = parsed.hostname
            if host:
                dns_ok, _, _, _ = verify_dns(host)
                if not dns_ok:
                    # DNS record not yet propagated or removed
                    # We should wait
                    status = "STARTING_DNS"

    # Always block if not RUNNING
    if status == "RUNNING":
        return
    
    if status in ["POWEROFF", "REBUILDING", "STARTING_DNS"]:
        show_startup_dialog(config, "STARTING" if status == "STARTING_DNS" else status)
        st.stop()
    else:
        # Unexpected state, but still block as it's not RUNNING
        st.warning(f"Database is in an unexpected state: {status}. Access is blocked for safety.")
        st.stop()
