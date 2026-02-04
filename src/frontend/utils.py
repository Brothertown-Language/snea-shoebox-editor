# Copyright (c) 2026 Brothertown Language
import streamlit as st
import socket
import os
import platform
import shutil
import psutil
from urllib.parse import urlparse
from sqlalchemy import text

def get_db_host_port():
    """Extracts host and port from Streamlit secrets or environment."""
    try:
        from src.database import get_db_url
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
        from src.database import get_session
        session = get_session()
        try:
            # Simple query to test connection
            session.execute(text("SELECT 1"))
            
            # Check for pgvector
            pgvector_check = session.execute(text("SELECT 1 FROM pg_extension WHERE extname = 'vector'")).fetchone()
            capabilities = {"pgvector": bool(pgvector_check)}
            
            return True, "Connected Successfully", capabilities
        finally:
            session.close()
    except Exception as e:
        return False, str(e), {}

def get_git_info():
    """Gathers information about the current git state."""
    import subprocess
    info = {}
    try:
        # Commit hash
        info["Commit"] = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], stderr=subprocess.STDOUT).decode().strip()
        # Branch
        info["Branch"] = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], stderr=subprocess.STDOUT).decode().strip()
        # Last commit date
        info["Date"] = subprocess.check_output(["git", "log", "-1", "--format=%cd"], stderr=subprocess.STDOUT).decode().strip()
    except Exception:
        info["Error"] = "Not a git repository or git not installed"
    return info

def get_env_info():
    """Gathers information about the environment."""
    info = {
        "Python Version": platform.python_version(),
        "Platform": platform.platform(),
        "Processor": platform.processor(),
        "Hostname": socket.gethostname(),
        "Streamlit Version": st.__version__
    }
    # Add git info
    git = get_git_info()
    if "Error" not in git:
        info["Git Commit"] = git["Commit"]
        info["Git Branch"] = git["Branch"]
        info["Git Date"] = git["Date"]
    return info

def get_masked_env_vars():
    """Returns a dictionary of environment variables with sensitive values masked."""
    masked = {}
    sensitive_keys = ["SECRET", "PASSWORD", "KEY", "TOKEN", "AUTH", "DATABASE_URL", "PGURL"]
    for key, value in os.environ.items():
        if any(sk in key.upper() for sk in sensitive_keys):
            masked[key] = "********"
        else:
            masked[key] = value
    return masked

def get_filesystem_info():
    """Gathers information about the filesystem."""
    paths_to_check = ["/", "/tmp", os.getcwd()]
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
