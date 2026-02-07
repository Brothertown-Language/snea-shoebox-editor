# Copyright (c) 2026 Brothertown Language
"""
Authentication utilities for GitHub OAuth.
"""
import streamlit as st
import requests
from typing import Optional, Dict, Any, List

def is_identity_synchronized() -> bool:
    """
    Check if all critical GitHub identity information is present in the session state.
    """
    return all(key in st.session_state for key in ["user_info", "user_orgs", "user_teams"])

def fetch_github_user_info(access_token: str) -> bool:
    """
    Fetch user info, organizations, and teams from GitHub and store in session state.
    Returns True if successful and authorized, False otherwise.
    """
    print("DEBUG: Fetching GitHub user info...", flush=True)
    headers = {
        "Authorization": f"token {access_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    base_url = st.secrets["github_oauth"]["user_info_url"]

    try:
        # Fetch user profile
        user_response = requests.get(base_url, headers=headers)
        user_response.raise_for_status()
        user_info = user_response.json()
        st.session_state["user_info"] = user_info
        
        # Log to console
        print(f"INFO: Fetched GitHub user info for: {user_info.get('login')}", flush=True)

        # Fetch organizations
        orgs_response = requests.get(f"{base_url}/orgs", headers=headers)
        orgs_response.raise_for_status()
        st.session_state["user_orgs"] = orgs_response.json()

        # Fetch teams
        teams_response = requests.get(f"{base_url}/teams", headers=headers)
        teams_response.raise_for_status()
        user_teams = teams_response.json()
        st.session_state["user_teams"] = user_teams

        # Fetch user emails to get the primary email
        emails_response = requests.get(f"{base_url}/emails", headers=headers)
        emails_response.raise_for_status()
        emails = emails_response.json()
        
        primary_email = None
        for email_record in emails:
            if email_record.get("primary") and email_record.get("verified"):
                primary_email = email_record.get("email")
                break
        
        # Fallback to the email in user_info if no primary/verified found
        if not primary_email:
            primary_email = user_info.get("email")

        # Verify team membership
        # Must be in Brothertown-Language / proto-SNEA
        is_authorized = False
        for team in user_teams:
            team_name = team.get("name")
            org_info = team.get("organization", {})
            org_login = org_info.get("login")

            if team_name == "proto-SNEA" and org_login == "Brothertown-Language":
                is_authorized = True
                break

        if not is_authorized:
            print(f"DEBUG: User not authorized. Teams: {[t.get('name') for t in user_teams]}", flush=True)
            st.session_state["is_unauthorized"] = True
            return False

        # If authorized, sync user to database
        if primary_email:
            sync_user_to_db(user_info, primary_email)
            
            # Log the login activity
            print(f"DEBUG: User logged in: {primary_email}", flush=True)
            log_user_activity(primary_email, "login", "User logged in via GitHub OAuth")
        else:
            st.warning("Could not determine user email. Audit trail might be limited.")

        return True

    except Exception as e:
        st.error(f"Failed to fetch user information from GitHub: {e}")
        return False

def log_user_activity(email: str, action: str, details: Optional[str] = None) -> None:
    """
    Log a user activity to the database.
    """
    from src.database import get_session, UserActivityLog
    
    session = get_session()
    try:
        log = UserActivityLog(
            user_email=email,
            action=action,
            details=details
        )
        session.add(log)
        session.commit()
    except Exception as e:
        session.rollback()
        # We don't want to block the user if logging fails, but we should know
        print(f"Failed to log user activity: {e}", flush=True)
    finally:
        session.close()

def sync_user_to_db(user_info: Dict[str, Any], email: str) -> None:
    """
    Update or create the user record in the database.
    """
    from src.database import get_session, User
    from sqlalchemy.sql import func
    import datetime

    github_id = user_info.get("id")
    username = user_info.get("login")
    full_name = user_info.get("name")

    if not github_id or not username:
        return

    session = get_session()
    try:
        # Try to find user by github_id (primary lookup as per issue)
        user = session.query(User).filter_by(github_id=github_id).first()
        
        if user:
            # Update existing user
            user.email = email
            user.username = username
            user.full_name = full_name
            user.last_login = func.now()
        else:
            # Check if email is already used by another account (to avoid unique constraint violation)
            existing_email_user = session.query(User).filter_by(email=email).first()
            if existing_email_user:
                # If email exists but different github_id, we might have an identity conflict.
                # For now, we update the existing account's github_id if it's missing or handle as new.
                # Given the requirement "update the user record using the github id number",
                # if we don't find it by github_id, it's essentially a new user or a migration.
                st.warning(f"Email {email} is already associated with another account. Please contact admin.")
                return

            # Create new user
            user = User(
                email=email,
                username=username,
                github_id=github_id,
                full_name=full_name,
                last_login=func.now()
            )
            session.add(user)
        
        session.commit()
    except Exception as e:
        session.rollback()
        st.error(f"Failed to sync user to database: {e}")
        # Log to stderr as well for visibility in logs
        print(f"ERROR: sync_user_to_db failed: {e}", flush=True)
    finally:
        session.close()
