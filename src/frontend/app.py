# Copyright (c) 2026 Brothertown Language
import streamlit as st
from sqlalchemy import text
import sys
import os
import platform
import socket
import shutil
import psutil
from urllib.parse import urlparse

def get_db_host_port():
    """Extracts host and port from Streamlit secrets or environment."""
    try:
        from src.backend.database import get_db_url
        url = get_db_url()
        
        if url:
            parsed = urlparse(url)
            # For Unix socket paths in pgserver, hostname might be empty
            return parsed.hostname or "localhost", parsed.port or 5432
    except Exception:
        pass
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
        from src.backend.database import get_db_url
        db_url = get_db_url()
        if not db_url:
            return False, "Database URL not found", {}
            
        # Streamlit handles the connection using secrets defined under [connections.postgresql]
        # But if we auto-started, we might need to use the URL directly
        capabilities = {}
        if os.getenv("DATABASE_URL") == db_url:
            from sqlalchemy import create_engine
            engine = create_engine(db_url)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1;"))
                # Check for pgvector
                res = conn.execute(text("SELECT count(*) FROM pg_extension WHERE extname = 'vector';")).scalar()
                capabilities["pgvector"] = res > 0
        else:
            conn = st.connection("postgresql", type="sql")
            with conn.session as s:
                s.execute(text("SELECT 1;"))
                # Check for pgvector
                res = s.execute(text("SELECT count(*) FROM pg_extension WHERE extname = 'vector';")).scalar()
                capabilities["pgvector"] = res > 0
        return True, "Connection Successful", capabilities
    except Exception as e:
        return False, str(e), {}

def get_env_info():
    """Gathers information about the execution environment."""
    from src.backend.database import _is_production
    
    is_prod = _is_production()
    info = {
        "Environment": "Production (Streamlit Cloud)" if is_prod else "Local Development",
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

def get_filesystem_info():
    """Gathers information about the filesystem."""
    paths_to_check = [".", "/tmp"]
    fs_info = {}
    
    for path in paths_to_check:
        abs_path = os.path.abspath(path)
        try:
            usage = shutil.disk_usage(abs_path)
            fs_info[abs_path] = {
                "Total": f"{usage.total / (1024**3):.2f} GB",
                "Used": f"{usage.used / (1024**3):.2f} GB",
                "Free": f"{usage.free / (1024**3):.2f} GB",
                "Writable": os.access(abs_path, os.W_OK)
            }
        except Exception as e:
            fs_info[abs_path] = {"Error": str(e)}
            
    return fs_info

def get_hardware_info():
    """Gathers information about the hardware."""
    try:
        cpu_count = psutil.cpu_count(logical=True)
        cpu_freq = psutil.cpu_freq()
        mem = psutil.virtual_memory()
        
        info = {
            "CPU Count (Logical)": cpu_count,
            "Memory Total": f"{mem.total / (1024**3):.2f} GB",
            "Memory Available": f"{mem.available / (1024**3):.2f} GB",
            "Memory Percent Used": f"{mem.percent}%"
        }
        
        if cpu_freq:
            info["CPU Frequency"] = f"{cpu_freq.current:.2f} MHz"
            
        return info
    except Exception as e:
        return {"Error": str(e)}


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
        is_valid, message, caps = check_db_connection()
        
        if is_valid:
            st.success("✅ SQL Connection: VALID")
            st.write("The database is reachable and responding to queries.")
            
            # Display Capabilities
            if caps.get("pgvector"):
                st.write("✅ **Capability: pgvector enabled**")
            else:
                st.warning("⚠️ **Capability: pgvector NOT enabled**")
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
        st.subheader("Hardware Inspection")
        hw_info = get_hardware_info()
        if "Error" in hw_info:
            st.error(f"Error gathering hardware info: {hw_info['Error']}")
        else:
            for key, value in hw_info.items():
                st.text(f"{key}: {value}")

        st.divider()
        st.subheader("Filesystem Inspection")
        fs_info = get_filesystem_info()
        for path, details in fs_info.items():
            st.markdown(f"**Path: `{path}`**")
            if "Error" in details:
                st.error(f"Error: {details['Error']}")
            else:
                cols = st.columns(2)
                cols[0].text(f"Total: {details['Total']}")
                cols[0].text(f"Used: {details['Used']}")
                cols[1].text(f"Free: {details['Free']}")
                writable_str = "✅ Writable" if details["Writable"] else "❌ Read-only"
                cols[1].text(f"Access: {writable_str}")

    st.divider()
    st.info("The application is being prepared for further development.")

if __name__ == "__main__":
    main()
