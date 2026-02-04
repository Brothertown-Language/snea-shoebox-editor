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
    """Verifies DNS resolution for the given host (IPv4 and IPv6)."""
    if not host:
        return False, "No host provided", [], []
    
    ipv4_ips = []
    ipv6_ips = []
    
    # Try IPv4
    try:
        _, _, ipv4_ips = socket.gethostbyname_ex(host)
    except Exception:
        pass
        
    # Try IPv6
    try:
        addr_info = socket.getaddrinfo(host, None, socket.AF_INET6)
        ipv6_ips = list(set(info[4][0] for info in addr_info))
    except Exception:
        pass
        
    if ipv4_ips or ipv6_ips:
        return True, "DNS Resolution Successful", ipv4_ips, ipv6_ips
    else:
        return False, "DNS Resolution Failed for both IPv4 and IPv6", [], []

def verify_reachability(host, port):
    """Verifies socket reachability for the given host and port (prefers IPv4, checks IPv6)."""
    if not host or not port:
        return False, "No host or port provided", False, False

    ipv4_ok = False
    ipv6_ok = False
    
    # Check IPv4
    try:
        # socket.create_connection uses the first address returned by getaddrinfo
        # To specifically test IPv4, we filter
        addr_v4 = socket.getaddrinfo(host, port, socket.AF_INET, socket.SOCK_STREAM)
        if addr_v4:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5)
                s.connect(addr_v4[0][4])
                ipv4_ok = True
    except Exception:
        pass

    # Check IPv6
    try:
        addr_v6 = socket.getaddrinfo(host, port, socket.AF_INET6, socket.SOCK_STREAM)
        if addr_v6:
            with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as s:
                s.settimeout(5)
                s.connect(addr_v6[0][4])
                ipv6_ok = True
    except Exception:
        pass

    if ipv4_ok or ipv6_ok:
        msg = "Socket Connection Successful"
        if ipv4_ok and ipv6_ok:
            msg += " (Dual Stack)"
        elif ipv4_ok:
            msg += " (IPv4 Only)"
        else:
            msg += " (IPv6 Only)"
        return True, msg, ipv4_ok, ipv6_ok
    else:
        return False, "Socket Connection Failed for both IPv4 and IPv6", False, False

def check_db_connection():
    """Checks the database connection and returns status and details."""
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
        dns_ok, dns_msg, ips_v4, ips_v6 = verify_dns(db_host)
        if dns_ok:
            st.write(f"✅ DNS Resolution: `{db_host}`")
            if ips_v4:
                st.info(f"IPv4 Addresses: {', '.join(ips_v4)}")
            if ips_v6:
                st.info(f"IPv6 Addresses: {', '.join(ips_v6)}")
        else:
            st.error(f"❌ DNS Resolution: FAILED")
            st.write(f"Details: `{dns_msg}`")

        # 2. Reachability Check
        reach_ok, reach_msg, v4_ok, v6_ok = verify_reachability(db_host, db_port)
        if reach_ok:
            st.write(f"✅ Socket Reachability: `{db_host}:{db_port}`")
            if v4_ok:
                st.success("IPv4: CONNECTED")
            else:
                st.warning("IPv4: FAILED")
                
            if v6_ok:
                st.success("IPv6: CONNECTED")
            else:
                st.warning("IPv6: FAILED (Expected on many local networks)")
        else:
            st.error(f"❌ Socket Reachability: FAILED")
            st.write(f"Details: `{reach_msg}`")

        # 3. SQL Connection Check (Only if previous checks pass or as final step)
        st.divider()
        st.subheader("SQL Health Check")
        is_valid, message = check_db_connection()
        
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
