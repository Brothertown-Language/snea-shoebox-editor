# Copyright (c) 2026 Brothertown Language
import streamlit as st
from sqlalchemy import text
import sys
import os
import platform

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
    st.info("The application is being prepared for further development.")

if __name__ == "__main__":
    main()
