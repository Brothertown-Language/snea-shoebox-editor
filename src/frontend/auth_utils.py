# Copyright (c) 2026 Brothertown Language
"""
Authentication utilities for GitHub OAuth.
"""
import streamlit as st
import requests
import datetime
from typing import Optional, Dict, Any, List
from src.database import get_session, User, UserActivityLog
from sqlalchemy.orm import Session

def sync_user_to_db(user_info: Dict[str, Any]) -> bool:
    """
    Upsert user information into the database and log the activity.
    """
    db: Session = get_session()
    try:
        github_id = user_info.get("id")
        email = user_info.get("email")
        username = user_info.get("login")
        name = user_info.get("name")

        if not github_id or not username:
            st.error("Invalid GitHub user data for database sync")
            return False

        # Fallback for email if not provided by GitHub (can happen if user has private email)
        if not email:
            email = f"{username}@github.com"

        user = db.query(User).filter(User.github_id == github_id).first()
        
        # Also check by email if github_id didn't match (handle legacy or cross-linked accounts)
        if not user:
            user = db.query(User).filter(User.email == email).first()

        now = datetime.datetime.now(datetime.timezone.utc)

        if not user:
            # Create new user
            user = User(
                github_id=github_id,
                email=email,
                username=username,
                full_name=name,
                last_login=now
            )
            db.add(user)
            action = "user_created"
        else:
            if not user.is_active:
                st.error("Account is disabled. Please contact an administrator.")
                return False
            
            # Update user info
            user.github_id = github_id # Ensure github_id is set if we found by email
            user.username = username
            if name:
                user.full_name = name
            
            # CRITICAL: Only update email if it doesn't look like a generated placeholder
            # and we have a fresh one from GitHub.
            if email and not email.endswith("@github.com"):
                user.email = email
            
            user.last_login = now
            action = "login"

        # Log activity
        log = UserActivityLog(
            user_email=email,
            action=action,
            details=f"User logged in via GitHub (ID: {github_id})",
            timestamp=now
        )
        db.add(log)
        
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        st.error(f"Database error during user sync: {e}")
        return False
    finally:
        db.close()

def fetch_github_user_info(access_token: str) -> bool:
    """
    Fetch user info, organizations, and teams from GitHub and store in session state.
    Returns True if successful and authorized, False otherwise.
    """
    headers = {
        "Authorization": f"token {access_token}",
        "Accept": "application/json"
    }
    base_url = st.secrets["github_oauth"]["user_info_url"]

    try:
        # Fetch user profile
        user_response = requests.get(base_url, headers=headers)
        user_response.raise_for_status()
        user_info = user_response.json()
        
        # Always fetch emails from /user/emails to ensure we get the primary verified email
        emails_response = requests.get(f"{base_url}/emails", headers=headers)
        if emails_response.status_code == 200:
            emails = emails_response.json()
            # Find the primary email
            for email_record in emails:
                if email_record.get("primary"):
                    user_info["email"] = email_record.get("email")
                    break
        
        st.session_state["user_info"] = user_info

        # Fetch organizations
        orgs_response = requests.get(f"{base_url}/orgs", headers=headers)
        orgs_response.raise_for_status()
        st.session_state["user_orgs"] = orgs_response.json()

        # Fetch teams
        teams_response = requests.get(f"{base_url}/teams", headers=headers)
        teams_response.raise_for_status()
        user_teams = teams_response.json()
        st.session_state["user_teams"] = user_teams

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
            st.session_state["is_unauthorized"] = True
            return False

        # Sync user to database
        if not sync_user_to_db(st.session_state["user_info"]):
            return False

        return True

    except Exception as e:
        st.error(f"Failed to fetch user information from GitHub: {e}")
        return False
