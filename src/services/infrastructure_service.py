# Copyright (c) 2026 Brothertown Language
# <!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
"""
Infrastructure Service for centralizing Aiven API management,
network diagnostics, and system inspection.
"""
import os
import platform
import shutil
import socket
import subprocess
import time
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

import psutil
import requests
from sqlalchemy import text


class InfrastructureService:
    """
    Service for managing infrastructure concerns: Aiven cloud database lifecycle,
    network/DNS/socket reachability checks, and system inspection.

    All methods are stateless and static. Streamlit UI (dialogs, spinners) is
    intentionally excluded — callers in the frontend layer handle presentation.
    """

    # ── Aiven API ──────────────────────────────────────────────────────

    @staticmethod
    def get_aiven_config() -> Optional[Dict[str, str]]:
        """Retrieve Aiven configuration from Streamlit secrets."""
        try:
            import streamlit as st
            if "aiven" in st.secrets:
                return {
                    "project": st.secrets["aiven"]["project_name"],
                    "service": st.secrets["aiven"]["service_name"],
                    "api_token": st.secrets["aiven"]["api_token"],
                }
        except Exception:
            pass
        return None

    @staticmethod
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
        except Exception:
            return None

    @staticmethod
    def get_service_status(config: Dict[str, str]) -> Optional[str]:
        """Get the current state of the Aiven service."""
        info = InfrastructureService.get_service_info(config)
        return info.get("state") if info else None

    @staticmethod
    def start_service(config: Dict[str, str]) -> bool:
        """Trigger the Aiven service to start (power on)."""
        url = f"https://api.aiven.io/v1/project/{config['project']}/service/{config['service']}"
        headers = {"Authorization": f"aivenv1 {config['api_token']}"}
        data = {"powered": True}

        try:
            response = requests.put(url, headers=headers, json=data, timeout=10)
            response.raise_for_status()
            return True
        except Exception:
            return False

    # ── Secrets Validation ─────────────────────────────────────────────

    @staticmethod
    def get_missing_secrets() -> List[str]:
        """
        Check for missing mandatory secrets.
        Returns a list of missing secret key paths (empty if all present).
        """
        import streamlit as st

        mandatory_secrets = ["aiven", "github_oauth", "connections"]
        missing: List[str] = []

        for secret in mandatory_secrets:
            try:
                if secret not in st.secrets:
                    missing.append(secret)
                else:
                    if secret == "aiven":
                        for k in ["project_name", "service_name", "api_token"]:
                            if k not in st.secrets["aiven"]:
                                missing.append(f"aiven.{k}")
                    elif secret == "github_oauth":
                        for k in ["client_id", "client_secret", "authorize_url", "token_url", "redirect_uri"]:
                            if k not in st.secrets["github_oauth"]:
                                missing.append(f"github_oauth.{k}")
                    elif secret == "connections":
                        if "postgresql" not in st.secrets["connections"] or "url" not in st.secrets["connections"]["postgresql"]:
                            missing.append("connections.postgresql.url")
            except Exception:
                missing.append(secret)

        return missing

    # ── Database Liveness ──────────────────────────────────────────────

    @staticmethod
    def check_db_alive() -> Tuple[bool, Optional[str]]:
        """
        Check whether the database is alive and reachable.
        Returns (is_alive, effective_status) where effective_status is the
        Aiven service state (or a synthetic state like 'STARTING_DNS').
        Only meaningful in production; returns (True, 'RUNNING') for local dev.
        """
        from src.database import is_production

        if not is_production():
            return True, "RUNNING"

        config = InfrastructureService.get_aiven_config()
        if not config:
            return True, None  # No Aiven config — nothing to manage

        status = InfrastructureService.get_service_status(config)

        if status == "RUNNING":
            from src.database import get_db_url
            url = get_db_url()
            if url:
                parsed = urlparse(url)
                host = parsed.hostname
                if host:
                    dns_ok, _, _, _ = InfrastructureService.verify_dns(host)
                    if not dns_ok:
                        return False, "STARTING_DNS"
            return True, "RUNNING"

        return False, status

    # ── Network / DNS / Socket Checks ──────────────────────────────────

    @staticmethod
    def get_db_host_port() -> Tuple[Optional[str], Optional[int]]:
        """Extract host and port from the database URL."""
        try:
            from src.database import get_db_url
            import urllib.parse as _urlparse

            url = get_db_url()
            if url:
                parsed = urlparse(url)
                query = _urlparse.parse_qs(parsed.query)
                if "host" in query:
                    return query["host"][0], 0
                return parsed.hostname or "localhost", parsed.port or 5432
        except Exception:
            pass
        return None, None

    @staticmethod
    def verify_dns(host: str) -> Tuple[bool, str, List[str], List[str]]:
        """Verify DNS resolution for the given host (IPv4 and IPv6)."""
        if not host:
            return False, "No host provided", [], []

        ipv4_ips: List[str] = []
        ipv6_ips: List[str] = []

        try:
            _, _, ipv4_ips = socket.gethostbyname_ex(host)
        except Exception:
            pass

        try:
            addr_info = socket.getaddrinfo(host, None, socket.AF_INET6)
            ipv6_ips = list(set(info[4][0] for info in addr_info))
        except Exception:
            pass

        if ipv4_ips or ipv6_ips:
            return True, "DNS Resolution Successful", ipv4_ips, ipv6_ips
        return False, "DNS Resolution Failed for both IPv4 and IPv6", [], []

    @staticmethod
    def verify_reachability(host: str, port: int) -> Tuple[bool, str, bool, bool]:
        """
        Verify socket reachability for the given host and port.
        Handles both TCP (host + port) and Unix sockets (path + port=0).
        """
        if not host:
            return False, "No host provided", False, False

        # Unix socket
        if port == 0 or host.startswith("/"):
            try:
                socket_path = host
                if os.path.isdir(host):
                    for item in os.listdir(host):
                        if item.startswith(".s.PGSQL.") and not item.endswith(".lock"):
                            socket_path = os.path.join(host, item)
                            break

                if os.path.exists(socket_path):
                    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
                        s.settimeout(5)
                        s.connect(socket_path)
                        return True, f"Unix Socket Reachable: {os.path.basename(socket_path)}", True, False
                else:
                    return False, f"Unix Socket Path Not Found: {socket_path}", False, False
            except Exception as e:
                return False, f"Unix Socket Connection Failed: {e}", False, False

        if not port:
            return False, "No port provided for TCP connection", False, False

        ipv4_ok = False
        ipv6_ok = False

        try:
            addr_v4 = socket.getaddrinfo(host, port, socket.AF_INET, socket.SOCK_STREAM)
            if addr_v4:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(5)
                    s.connect(addr_v4[0][4])
                    ipv4_ok = True
        except Exception:
            pass

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
        return False, "Socket Connection Failed for both IPv4 and IPv6", False, False

    @staticmethod
    def check_db_connection() -> Tuple[bool, str, Dict[str, bool]]:
        """Check the database connection and return status and capabilities."""
        try:
            from src.database import get_session
            session = get_session()
            try:
                session.execute(text("SELECT 1"))
                pgvector_check = session.execute(
                    text("SELECT 1 FROM pg_extension WHERE extname = 'vector'")
                ).fetchone()
                capabilities = {"pgvector": bool(pgvector_check)}
                return True, "Connected Successfully", capabilities
            finally:
                session.close()
        except Exception as e:
            # Database operation failures are fatal; do not swallow.
            raise

    # ── System Inspection ──────────────────────────────────────────────

    @staticmethod
    def get_git_info() -> Dict[str, str]:
        """Gather information about the current git state."""
        info: Dict[str, str] = {}
        try:
            info["Commit"] = subprocess.check_output(
                ["git", "rev-parse", "--short", "HEAD"], stderr=subprocess.STDOUT
            ).decode().strip()
            info["Branch"] = subprocess.check_output(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"], stderr=subprocess.STDOUT
            ).decode().strip()
            info["Date"] = subprocess.check_output(
                ["git", "log", "-1", "--format=%cd"], stderr=subprocess.STDOUT
            ).decode().strip()
        except Exception:
            info["Error"] = "Not a git repository or git not installed"
        return info

    @staticmethod
    def get_env_info() -> Dict[str, str]:
        """Gather information about the environment."""
        import streamlit as st

        info = {
            "Python Version": platform.python_version(),
            "Platform": platform.platform(),
            "Processor": platform.processor(),
            "Hostname": socket.gethostname(),
            "Streamlit Version": st.__version__,
        }
        git = InfrastructureService.get_git_info()
        if "Error" not in git:
            info["Git Commit"] = git["Commit"]
            info["Git Branch"] = git["Branch"]
            info["Git Date"] = git["Date"]
        return info

    @staticmethod
    def get_filesystem_info() -> Dict[str, Dict[str, Any]]:
        """Gather information about the filesystem."""
        paths_to_check = ["/", "/tmp", os.getcwd()]
        fs_info: Dict[str, Dict[str, Any]] = {}
        for path in paths_to_check:
            abs_path = os.path.abspath(path)
            try:
                usage = shutil.disk_usage(abs_path)
                fs_info[abs_path] = {
                    "Total": f"{usage.total / (1024**3):.2f} GB",
                    "Used": f"{usage.used / (1024**3):.2f} GB",
                    "Free": f"{usage.free / (1024**3):.2f} GB",
                    "Writable": os.access(abs_path, os.W_OK),
                }
            except Exception as e:
                fs_info[abs_path] = {"Error": str(e)}
        return fs_info

    @staticmethod
    def get_hardware_info() -> Dict[str, Any]:
        """Gather information about the hardware."""
        try:
            cpu_count = psutil.cpu_count(logical=True)
            cpu_freq = psutil.cpu_freq()
            mem = psutil.virtual_memory()

            info: Dict[str, Any] = {
                "CPU Count (Logical)": cpu_count,
                "Memory Total": f"{mem.total / (1024**3):.2f} GB",
                "Memory Available": f"{mem.available / (1024**3):.2f} GB",
                "Memory Percent Used": f"{mem.percent}%",
            }

            if cpu_freq:
                info["CPU Frequency"] = f"{cpu_freq.current:.2f} MHz"

            return info
        except Exception as e:
            return {"Error": str(e)}
