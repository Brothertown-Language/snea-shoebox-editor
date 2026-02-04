# Copyright (c) 2026 Brothertown Language
import streamlit as st
from sqlalchemy import text
import sys
import os
import glob
import platform
import fnmatch

try:
    import tomllib
except ImportError:
    import tomli as tomllib

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

def is_streamlit_cloud():
    """Detects if the app is running on Streamlit Community Cloud."""
    # Streamlit Cloud sets certain environment variables
    # Check for common ones
    return (
        os.environ.get("STREAMLIT_RUNTIME_EXECUTABLE") == "streamlit" 
        and os.environ.get("HOME") == "/home/appuser"
    ) or os.path.exists("/app/snea-shoebox-editor")

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

def verify_deployment_exclusions():
    """
    Verifies that files and directories listed in .streamlit/config.toml
    under [server] exclude_pattern are not present in the current environment.
    
    Returns a list of (pattern, exists, type) tuples.
    """
    results = []
    config_file = ".streamlit/config.toml"
    
    if not os.path.exists(config_file):
        return results

    try:
        with open(config_file, "rb") as f:
            config = tomllib.load(f)
            
        exclude_pattern = config.get("server", {}).get("exclude_pattern", "")
        if not exclude_pattern:
            return results
            
        # Patterns are comma-separated
        patterns = [p.strip() for p in exclude_pattern.split(",")]
            
        for pattern in patterns:
            # Remove trailing slash and recursive glob marker for existence check
            clean_pattern = pattern.rstrip('/').replace('/**', '')
            
            # Use glob to handle patterns
            matches = glob.glob(clean_pattern)
            
            if matches:
                for match in matches:
                    item_type = "Dir" if os.path.isdir(match) else "File"
                    results.append((pattern, True, item_type))
            else:
                # If no matches, it's successfully ignored (absent)
                results.append((pattern, False, "Unknown"))
                
    except Exception as e:
        st.error(f"Error reading .streamlit/config.toml: {e}")
        
    return results

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
        # Health Check Section
        st.subheader("Database Health Check")
        is_valid, message = check_supabase_connection()
        
        if is_valid:
            st.success("✅ Supabase Connection: VALID")
            st.write("The database is reachable and responding.")
        else:
            st.error("❌ Supabase Connection: INVALID")
            st.write(f"Error Details: `{message}`")
            st.info("Check your Streamlit Cloud Secrets.")

    with col2:
        # Environment Info Section
        st.subheader("Environment Information")
        env_info = get_env_info()
        for key, value in env_info.items():
            st.text(f"{key}: {value}")

    st.divider()

    # Deployment Integrity Section
    st.subheader("Deployment Integrity (Exclusion Check)")
    st.write("Verifying that development-only files are excluded from the deployment.")
    
    exclusion_results = verify_deployment_exclusions()
    is_cloud = is_streamlit_cloud()
    
    if not exclusion_results:
        st.warning("No deployment exclusion patterns found in `.streamlit/config.toml`.")
    else:
        found_any = any(exists for _, exists, _ in exclusion_results)
        
        if found_any:
            if is_cloud:
                st.error("❌ Warning: Some development files are present in this PRODUCTION environment.")
                icon = "❌"
                status_msg = "These files should be excluded from production via `server.exclude_pattern`."
            else:
                st.info("ℹ️ Development files are present (Normal for local development).")
                icon = "📁"
                status_msg = "Note: These files are expected to be present during local development."

            # Show details in an expander
            with st.expander("Show Detailed Exclusion Report"):
                # Filter only those that exist
                existing_items = [r for r in exclusion_results if r[1]]
                for pattern, exists, item_type in existing_items:
                    st.write(f"{icon} `{pattern}` ({item_type}) is **PRESENT**")
                
                st.divider()
                st.write(status_msg)
        else:
            st.success("✅ All files in `server.exclude_pattern` are successfully excluded.")

    st.divider()
    st.info("The application is being prepared for further development.")

if __name__ == "__main__":
    main()
