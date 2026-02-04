# Copyright (c) 2026 Brothertown Language
import streamlit as st
from sqlalchemy import text
import sys
import os
import platform
import socket
from urllib.parse import urlparse

def get_db_host_port():
    """Extracts host and port from Streamlit secrets."""
    try:
        url = st.secrets["connections"]["postgresql"]["url"]
        parsed = urlparse(url)
        return parsed.hostname, parsed.port or 5432
    except Exception:
        return None, None

def verify_dns(host):
    """Verifies DNS resolution for the given host."""
    if not host:
        return False, "No host provided", []
    try:
        name, aliases, ip_list = socket.gethostbyname_ex(host)
        return True, "DNS Resolution Successful", ip_list
    except Exception as e:
        return False, f"DNS Resolution Failed: {e}", []

def verify_reachability(host, port):
    """Verifies socket reachability for the given host and port."""
    if not host or not port:
        return False, "No host or port provided"
    try:
        with socket.create_connection((host, port), timeout=5):
            return True, f"Socket Connection Successful to {host}:{port}"
    except Exception as e:
        return False, f"Socket Connection Failed: {e}"

def check_supabase_connection():
    """Checks the Supabase connection and returns status and details."""
    try:
        # Streamlit handles the connection using secrets defined under [connections.postgresql]
        conn = st.connection("postgresql", type="sql")
        with conn.session as s:
            s.execute(text("SELECT 1;"))
        return True, "Connection Successful"
    except Exception as e:
        return False, str(e)

def get_env_info():
    """Gathers information about the execution environment."""
    info = {
        "Python Version": sys.version.split()[0],
        "Operating System": f"{platform.system()} {platform.release()}",
        "Streamlit Version": st.__version__,
        "Executable": sys.executable,
    }
    
    # Check for uv usage
    # Streamlit Cloud with uv support usually sets certain markers or we can infer from the path
    is_uv = "uv" in sys.executable or os.path.exists("uv.lock")
    info["Using uv"] = "Yes" if is_uv else "No (Standard pip/venv)"
    
    return info


def main():
    st.set_page_config(
        page_title="SNEA Shoebox Editor",
        page_icon="📚",
        layout="wide"
    )
    st.title("SNEA Shoebox Editor - System Status")
    
    st.write("Welcome to the SNEA Online Shoebox Editor. Below is the current system status.")

    col1, col2 = st.columns(2)

    with col1:
        # Database Infrastructure Checklist
        st.subheader("Database Connectivity Checklist")
        
        db_host, db_port = get_db_host_port()
        
        # 1. DNS Check
        dns_ok, dns_msg, ips = verify_dns(db_host)
        if dns_ok:
            st.write(f"✅ DNS Resolution: `{db_host}`")
            st.info(f"Resolved IPs: {', '.join(ips)}")
        else:
            st.error(f"❌ DNS Resolution: FAILED")
            st.write(f"Details: `{dns_msg}`")

        # 2. Reachability Check
        reach_ok, reach_msg = verify_reachability(db_host, db_port)
        if reach_ok:
            st.write(f"✅ Socket Reachability: `{db_host}:{db_port}` is reachable.")
        else:
            st.error(f"❌ Socket Reachability: FAILED")
            st.write(f"Details: `{reach_msg}`")

        # 3. SQL Connection Check (Only if previous checks pass or as final step)
        st.divider()
        st.subheader("SQL Health Check")
        is_valid, message = check_supabase_connection()
        
        if is_valid:
            st.success("✅ SQL Connection: VALID")
            st.write("The database is reachable and responding to queries.")
        else:
            st.error("❌ SQL Connection: INVALID")
            st.write(f"Error Details: `{message}`")
            st.info("Check your Streamlit Cloud Secrets and Database status.")

    with col2:
        # Environment Info Section
        st.subheader("Environment Information")
        env_info = get_env_info()
        for key, value in env_info.items():
            st.text(f"{key}: {value}")

    st.divider()
    st.info("The application is being prepared for further development.")

if __name__ == "__main__":
    main()
