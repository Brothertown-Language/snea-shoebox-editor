# Copyright (c) 2026 Brothertown Language
import streamlit as st
from sqlalchemy import text

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

def main():
    st.set_page_config(
        page_title="SNEA Shoebox Editor",
        page_icon="📚",
        layout="wide"
    )
    st.title("SNEA Shoebox Editor - Health Check")
    
    st.write("Welcome to the SNEA Online Shoebox Editor. Below is the current system status.")

    # Health Check Section
    st.subheader("System Health Check")
    
    is_valid, message = check_supabase_connection()
    
    if is_valid:
        st.success("✅ Supabase Connection: VALID")
        st.write("The database is reachable and responding.")
    else:
        st.error("❌ Supabase Connection: INVALID")
        st.write(f"Error Details: `{message}`")
        st.info("Check your Streamlit Cloud Secrets and ensure the PostgreSQL URL is correct.")

    st.divider()
    st.info("The application is being prepared for further development.")

if __name__ == "__main__":
    main()
