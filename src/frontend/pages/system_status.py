# Copyright (c) 2026 Brothertown Language
"""
AI Coding Defaults:
- Strict Typing: Mandatory for all function signatures and variable declarations.
- Lazy Initialization: Imports inside functions for Streamlit pages to optimize loading.
- Single Responsibility: Each function/method must have one clear purpose.
- Standalone Execution: Page files must include a main execution block.
- Background Execution: MANDATORY use of nohup for all Streamlit runs (e.g. scripts/start_streamlit.sh).
"""
def system_status():
    import streamlit as st
    import os
    from src.frontend.utils import (
        get_db_host_port, verify_dns, verify_reachability, 
        check_db_connection, get_env_info, get_hardware_info, 
        get_filesystem_info
    )
    st.title("SNEA Shoebox Editor - System Status")
    st.write("Welcome to the SNEA Online Shoebox Editor. Below is the current system status.")

    col1, col2 = st.columns(2)

    with col1:
        # Database Infrastructure Checklist
        st.subheader("Database Connectivity Checklist")
        
        from src.database import is_production
        from src.aiven_utils import get_aiven_config, get_service_status, get_service_info
        
        is_prod = is_production()
        env_label = "Production" if is_prod else "Local Test"
        st.write(f"Environment: **{env_label}**")
        
        db_host, db_port = get_db_host_port()

        # Check Aiven Status if in production
        aiven_status = None
        if is_prod:
            config = get_aiven_config()
            if config:
                info = get_service_info(config)
                if info:
                    aiven_status = info.get("state")
                    
                    with st.expander("Aiven Database Details", expanded=(aiven_status != "RUNNING")):
                        st.write(f"Service: `{info.get('service_name')}`")
                        st.write(f"State: **{aiven_status}**")
                        st.write(f"Plan: `{info.get('plan')}`")
                        st.write(f"Cloud: `{info.get('cloud_name')}`")
                        
                        pg_info = info.get("service_integrations", [])
                        # Some info might be in 'metadata' or 'components' depending on service type
                        # For Postgres:
                        user_config = info.get("user_config", {})
                        if user_config:
                            version = user_config.get("pg_version")
                            if version:
                                st.write(f"PostgreSQL Version: `{version}`")
                            
                            backup_hour = user_config.get("backup_hour")
                            if backup_hour is not None:
                                st.write(f"Daily Backup Hour: `{backup_hour}:00 UTC`")
                        
                        # Show some stats if available
                        metadata = info.get("metadata", {})
                        if metadata:
                            # Not all services have these in metadata, but some do
                            pass
                                
                        if aiven_status and aiven_status != "RUNNING":
                            st.warning(f"⚠️ Aiven Service Status: **{aiven_status}**")
                            st.info("The database is currently starting up or powering on. DNS and Socket checks may fail until it is fully RUNNING.")
        
        # Mask host for display
        masked_host = "Database Host [REDACTED]"
        if db_host:
            if "localhost" in db_host or "127.0.0.1" in db_host:
                masked_host = f"Local Host (`{db_host}`)"
            else:
                parts = db_host.split('.')
                if len(parts) > 2:
                    masked_host = f"`{parts[0][:3]}...{parts[-2]}.{parts[-1]}`"
                else:
                    masked_host = f"`{db_host[:3]}...`"

        # 1. DNS Check
        is_unix_socket = (db_host and db_host.startswith('/')) or (not db_host and db_port == 0)
        
        if is_unix_socket:
            st.write("✅ Database Connection: Unix Socket (Local)")
            dns_ok = True # Skip DNS for Unix socket
        else:
            dns_ok, dns_msg, ips_v4, ips_v6 = verify_dns(db_host)
            if dns_ok:
                st.write(f"✅ DNS Resolution: {masked_host}")
                if ips_v4:
                    st.info(f"IPv4: {len(ips_v4)} address(es) found [REDACTED]")
                if ips_v6:
                    st.info(f"IPv6: {len(ips_v6)} address(es) found [REDACTED]")
            else:
                if aiven_status and aiven_status != "RUNNING":
                    st.warning(f"⚠️ DNS Resolution: WAITING (Service is {aiven_status})")
                else:
                    st.error(f"❌ DNS Resolution: FAILED")
                st.write(f"Details: DNS lookup failed for the configured host.")

        # 2. Reachability Check
        reach_ok, reach_msg, v4_ok, v6_ok = verify_reachability(db_host, db_port)
        if reach_ok:
            if is_unix_socket:
                st.write(f"✅ Socket Reachability: {reach_msg}")
            else:
                st.write(f"✅ Socket Reachability: {masked_host}")
                if v4_ok:
                    st.success("IPv4: CONNECTED")
                else:
                    st.warning("IPv4: FAILED")
                    
                if v6_ok:
                    st.success("IPv6: CONNECTED")
                else:
                    st.warning("IPv6: FAILED (Expected on many local networks)")
        else:
            if aiven_status and aiven_status != "RUNNING":
                st.warning(f"⚠️ Socket Reachability: WAITING (Service is {aiven_status})")
            else:
                st.error(f"❌ Socket Reachability: FAILED")
            st.write(f"Details: {reach_msg}")

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
            # Mask error message if it contains the DB URL
            masked_error = str(message)
            db_url = os.getenv("DATABASE_URL")
            if db_url and db_url in masked_error:
                masked_error = masked_error.replace(db_url, "[REDACTED_URL]")
            
            st.write(f"Error Details: `{masked_error}`")
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

if __name__ == "__main__":
    system_status()

