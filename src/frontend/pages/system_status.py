# Copyright (c) 2026 Brothertown Language
import streamlit as st
from src.frontend.utils import (
    get_db_host_port, verify_dns, verify_reachability, 
    check_db_connection, get_env_info, get_hardware_info, 
    get_filesystem_info, get_masked_env_vars
)

def system_status():
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
    st.subheader("Environment Variables")
    with st.expander("View Environment Variables"):
        env_vars = get_masked_env_vars()
        st.json(env_vars)
